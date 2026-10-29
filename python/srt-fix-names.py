#!/usr/bin/env python3
import re
import sys
import glob
from collections import Counter

SRT_DIR = '../srt/'

MISHEARD = r"(?:kerry|carry|carey|curie|currie|currier|kuri|kurry|curri|corri|kori|kari|cury|curried)"
PLACES = r"(castle|cottage|manor|condo|bunker|terrace)"

FIXES = [
  (re.compile(rf"\b(Adam) {MISHEARD}\b", re.I), lambda m: f"{m.group(1)} Curry"),
  (re.compile(rf"\b{MISHEARD}(\.| dot )com\b", re.I), lambda m: f"curry{m.group(1)}com"),
  (re.compile(rf"\b{MISHEARD} ?{PLACES}\b", re.I), lambda m: f"Curry {m.group(1).capitalize()}"),
  (re.compile(r"\bKurry\b"), lambda m: "Curry"),
  (re.compile(r"\bkurry\b"), lambda m: "curry"),
]

TIMING = re.compile(r"^\d\d:\d\d:\d\d[,.]\d{3} --> ")


def fixText(line, counts):
  for pattern, replace in FIXES:
    def counted(m):
      new = replace(m)
      if new != m.group(0):
        counts[f"{m.group(0)} -> {new}"] += 1
      return new
    line = pattern.sub(counted, line)
  return line


def main():
  dry = '--dry-run' in sys.argv
  files = [a for a in sys.argv[1:] if not a.startswith('--')] or sorted(glob.glob(f"{SRT_DIR}*/*.srt"))
  counts, changed = Counter(), 0
  for path in files:
    with open(path, encoding='utf-8') as fp:
      lines = fp.read().split('\n')
    out = [line if (line.strip().isdigit() or TIMING.match(line)) else fixText(line, counts) for line in lines]
    if out != lines:
      changed += 1
      if not dry:
        with open(path, 'w', encoding='utf-8') as fp:
          fp.write('\n'.join(out))
  for fix, n in counts.most_common():
    print(f"{n:5} {fix}")
  print(f"{sum(counts.values())} fixes in {changed} files" + (" (dry run)" if dry else ""))


if __name__ == '__main__':
  main()
