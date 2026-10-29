#!/usr/bin/env python3
import re
import sys
import json
import subprocess

SR = 32000
WINDOW = 5.0
HOP = 2.5
MUSIC_MIN = 0.5
SPEECH_MAX = 0.1
SEGMENT_MIN = 20.0
GAP_MERGE = 5.0
EDGE_KEEP = 6.0
LABELS = ['Speech', 'Music', 'Singing']
MUSIC_CUE = '[ Music ]'


def decode(path):
  import numpy as np
  raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'quiet', '-i', path, '-map', '0:a', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
  return np.frombuffer(raw, dtype=np.float32)


def analyse(audio_path, cache_path):
  import numpy as np
  import torch
  from panns_inference import AudioTagging, labels
  torch.set_num_threads(4)
  tagger = AudioTagging(checkpoint_path=None, device='cpu')
  ids = [labels.index(n) for n in LABELS]
  audio = decode(audio_path)
  size, hop = int(WINDOW * SR), int(HOP * SR)
  starts = list(range(0, max(1, len(audio) - size + 1), hop))
  scores = []
  for b in range(0, len(starts), 32):
    batch = np.stack([np.pad(audio[s:s + size], (0, max(0, size - len(audio[s:s + size])))) for s in starts[b:b + 32]])
    out, _ = tagger.inference(batch)
    scores.extend(np.round(out[:, ids], 3).tolist())
  with open(cache_path, 'w') as fp:
    json.dump({'audio': audio_path, 'duration': len(audio) / SR, 'window': WINDOW, 'hop': HOP, 'labels': LABELS, 'scores': scores}, fp)


def musicSegments(cache):
  hop, window = cache['hop'], cache['window']
  music = [s[1] > MUSIC_MIN and s[0] < SPEECH_MAX for s in cache['scores']]
  runs = []
  start = None
  for i, m in enumerate(music + [False]):
    if m and start is None:
      start = i
    if not m and start is not None:
      runs.append([start * hop + window / 4, (i - 1) * hop + window * 3 / 4])
      start = None
  merged = []
  for run in runs:
    if merged and run[0] - merged[-1][1] <= GAP_MERGE:
      merged[-1][1] = run[1]
    else:
      merged.append(run)
  return [r for r in merged if r[1] - r[0] >= SEGMENT_MIN]


TS = re.compile(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)')


def seconds(h, m, s, ms):
  return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def timestamp(t):
  ms = int(round(t * 1000))
  return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def readSRT(path):
  with open(path, encoding='utf-8') as fp:
    text = fp.read()
  cues = []
  for block in re.split(r'\n\s*\n', text.strip()):
    lines = block.split('\n')
    for i, line in enumerate(lines):
      m = TS.search(line)
      if m:
        cues.append([seconds(*m.groups()[:4]), seconds(*m.groups()[4:]), '\n'.join(lines[i + 1:]).strip()])
        break
  return cues


def apply(srt_path, cache_path, out_path=None):
  with open(cache_path) as fp:
    cache = json.load(fp)
  segments = musicSegments(cache)
  cues = readSRT(srt_path)
  result = []
  dropped = 0
  for cue in cues:
    middle = (cue[0] + cue[1]) / 2
    if any(a + EDGE_KEEP <= middle < b - EDGE_KEEP for a, b in segments):
      dropped += 1
      continue
    result.append(cue)
  for a, b in segments:
    before = [c for c in result if c[2] != MUSIC_CUE and c[1] <= (a + b) / 2]
    after = [c for c in result if c[2] != MUSIC_CUE and c[0] >= (a + b) / 2]
    start = max(a, before[-1][1]) if before else a
    end = min(b, after[0][0]) if after else b
    if end - start >= SEGMENT_MIN / 2:
      result.append([start, end, MUSIC_CUE])
  result.sort(key=lambda c: c[0])
  lines = []
  for i, (a, b, text) in enumerate(result, 1):
    lines.append(f"{i}\n{timestamp(a)} --> {timestamp(b)}\n{text}\n")
  with open(out_path or srt_path, 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(lines))
  return segments, dropped


def main():
  if len(sys.argv) == 4 and sys.argv[1] == 'analyse':
    analyse(sys.argv[2], sys.argv[3])
  elif len(sys.argv) in [4, 5] and sys.argv[1] == 'apply':
    segments, dropped = apply(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) == 5 else None)
    print(f"{sys.argv[2]}: {len(segments)} music segments, {round(sum(b - a for a, b in segments))} s, {dropped} cues replaced")
  else:
    print('Usage: srt-music.py analyse AUDIO CACHE.json | apply SRT CACHE.json [OUT]')
    sys.exit(2)


if __name__ == '__main__':
  main()
