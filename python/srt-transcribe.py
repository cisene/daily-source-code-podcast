#!/usr/bin/env python3
import sys
import subprocess
import numpy as np
from faster_whisper import WhisperModel


def timestamp(t):
  ms = int(round(t * 1000))
  return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def decode(path):
  raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'quiet', '-i', path, '-map', '0:a', '-ac', '1', '-ar', '16000', '-f', 'f32le', '-'], capture_output=True).stdout
  return np.frombuffer(raw, dtype=np.float32)


def main():
  if len(sys.argv) not in [3, 4]:
    print('Usage: srt-transcribe.py AUDIO OUT.srt [MODEL]')
    sys.exit(2)
  audio, out = sys.argv[1], sys.argv[2]
  model = WhisperModel(sys.argv[3] if len(sys.argv) == 4 else 'small', device='cpu', compute_type='int8', cpu_threads=4)
  segments, info = model.transcribe(decode(audio), language='en', beam_size=5)
  lines = []
  for i, s in enumerate(segments, 1):
    lines.append(f"{i}\n{timestamp(s.start)} --> {timestamp(s.end)}\n{s.text.strip()}\n")
  with open(out, 'w', encoding='utf-8') as fp:
    fp.write('\n'.join(lines))
  print(f"{audio}: {len(lines)} cues, {round(info.duration)} s")


if __name__ == '__main__':
  main()
