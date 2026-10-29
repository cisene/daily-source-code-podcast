#!/usr/bin/env python3
import sys
import json
import itertools
import subprocess
import numpy as np

BITRATES = {1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320], 2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160]}
RATES = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}
CONTEXT = 6


def header(b, i):
  if i + 4 > len(b) or b[i] != 0xFF or (b[i + 1] & 0xE0) != 0xE0:
    return None
  ver = (b[i + 1] >> 3) & 3
  layer = (b[i + 1] >> 1) & 3
  br = b[i + 2] >> 4
  sr = (b[i + 2] >> 2) & 3
  pad = (b[i + 2] >> 1) & 1
  if ver == 1 or layer != 1 or br in (0, 15) or sr == 3:
    return None
  rate = RATES[ver][sr]
  kbps = BITRATES[1 if ver == 3 else 2][br]
  size = (144000 * kbps // rate + pad) if ver == 3 else (72000 * kbps // rate + pad)
  mono = (b[i + 3] >> 6) == 3
  side = (17 if mono else 32) if ver == 3 else (9 if mono else 17)
  return size, (ver, rate), 4 + side + (0 if b[i + 1] & 1 else 2)


def chained(b, i, sig, n=3):
  for _ in range(n):
    h = header(b, i)
    if not h or h[1] != sig:
      return False
    i += h[0]
  return True


def decode(frames):
  data = b''.join(frames)
  r = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-f', 'mp3', '-i', 'pipe:', '-f', 's16le', '-ac', '1', '-'], input=data, capture_output=True)
  return np.frombuffer(r.stdout, dtype=np.int16).astype(np.float32), r.stderr.count(b'\n')


def score(before, frame, after, samples):
  pcm, errors = decode(before + [frame] + after)
  if len(pcm) < samples * (len(before) + 1):
    return 1e12
  rms = [np.sqrt(np.mean(pcm[k * samples:(k + 1) * samples] ** 2)) + 1 for k in range(len(pcm) // samples)]
  at = len(before)
  ctx = [rms[k] for k in range(len(rms)) if k not in (at, at + 1)]
  jump = max(rms[at:at + 2]) / (np.median(ctx) if ctx else 1)
  return errors * 1000 + jump


def silent(frame, side_end):
  return frame[:4] + bytes(len(frame) - 4)


def main():
  src, dst = sys.argv[1], sys.argv[2]
  b = open(src, 'rb').read()
  start = 0
  if b[:3] == b'ID3':
    start = 10 + ((b[6] & 0x7f) << 21 | (b[7] & 0x7f) << 14 | (b[8] & 0x7f) << 7 | (b[9] & 0x7f))
  while not chained(b, start, header(b, start)[1] if header(b, start) else None):
    start += 1
  sig = header(b, start)[1]
  end = len(b) - (128 if b[-128:-125] == b'TAG' else 0)
  samples = 1152 if sig[0] == 3 else 576

  frames, report = [], []
  i = start
  while i < end:
    h = header(b, i)
    if not h or h[1] != sig:
      j = i + 1
      while j < end and not chained(b, j, sig):
        j += 1
      report.append({'offset': i, 'action': 'skipped bytes', 'bytes': j - i})
      i = j
      continue
    size, _, side_end = h
    nxt = i + size
    if nxt >= end or chained(b, nxt, sig, 1):
      frames.append(b[i:min(nxt, end)])
      i = nxt
      continue
    missing = next((d for d in (1, 2) if chained(b, nxt - d, sig, 1)), None)
    if missing:
      short = b[i:nxt - missing]
      lfs = [p for p in range(4, len(short)) if short[p] == 0x0A]
      cands = list(itertools.combinations(lfs, missing))
      before = frames[-CONTEXT:]
      after = []
      k = nxt - missing
      for _ in range(CONTEXT):
        hh = header(b, k)
        if not hh or hh[1] != sig:
          break
        after.append(b[k:k + hh[0]])
        k += hh[0]
      best = None
      for positions in cands:
        frame = short
        for p in reversed(positions):
          frame = frame[:p] + b'\r' + frame[p:]
        s = score(before, frame, after, samples)
        if best is None or s < best[0]:
          best = (s, positions, frame)
      if best and best[0] < 1000:
        frames.append(best[2])
        report.append({'offset': i, 'frame': len(frames) - 1, 'action': 'CR restored', 'missing': missing, 'positions': list(best[1]), 'candidates': len(cands), 'score': round(float(best[0]), 2)})
      else:
        frames.append(silent(short + bytes(missing), side_end))
        report.append({'offset': i, 'frame': len(frames) - 1, 'action': 'silenced', 'missing': missing, 'candidates': len(cands), 'score': None if not best else round(float(best[0]), 2)})
      i = nxt - missing
      continue
    j = i + 1
    while j < end and not chained(b, j, sig):
      j += 1
    frames.append(silent(b[i:nxt], side_end) if nxt <= j else b[i:j])
    report.append({'offset': i, 'action': 'other break, silenced', 'bytes': j - i})
    i = j

  with open(dst, 'wb') as fp:
    fp.write(b[:start])
    fp.write(b''.join(frames))
    fp.write(b[end:])
  if len(sys.argv) > 3:
    with open(sys.argv[3], 'w') as fp:
      json.dump(report, fp, indent=1)
  counts = {}
  for r in report:
    counts[r['action']] = counts.get(r['action'], 0) + 1
  print(f"{src}: {len(frames)} frames, {counts}")


if __name__ == '__main__':
  main()
