#!/usr/bin/env python3
import re
import sys
import glob
import unicodedata
import importlib.util

EPISODE_DIR = '../yaml/episodes/'
INVISIBLE = {'­', '​', '‌', '‍', '⁠', '﻿'}


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


audio = load('audio', 'update-episodes-from-audio.py')


def cleanChar(ch):
  if ch == '\n':
    return ch
  if ch in INVISIBLE:
    return ''
  if ch == '\xa0' or unicodedata.category(ch) in ('Cc', 'Cf', 'Zl', 'Zp'):
    return ' '
  return ch


def cleanText(value):
  value = value.replace('\r\n', '\n').replace('\r', '\n')
  head, found, tail = value.partition('\\nDuration: ')
  if found:
    value = (head.rstrip() + '\n' if head.strip() else '') + 'Duration: ' + tail
  value = ''.join(cleanChar(ch) for ch in value)
  lines = []
  for line in value.split('\n'):
    indent = len(line) - len(line.lstrip(' '))
    lines.append(line[:indent] + re.sub(r" {2,}", ' ', line[indent:]).rstrip(' '))
  return '\n'.join(lines)


def clean(data, counts):
  if isinstance(data, dict):
    return {k: clean(v, counts) for k, v in data.items()}
  if isinstance(data, list):
    return [clean(v, counts) for v in data]
  if isinstance(data, str):
    new = cleanText(data)
    if new != data:
      counts['strings'] += 1
    return new
  return data


def main():
  write = '--write' in sys.argv
  counts = {'strings': 0}
  changed = 0
  paths = sorted(glob.glob(f"{EPISODE_DIR}*.yaml"))
  for path in paths:
    ep = audio.readYAML(path)
    new = clean(ep, counts)
    if new != ep:
      changed += 1
      if write:
        audio.writeYAML(path, new)
  print(f"{len(paths)} episodes, {changed} changed, {counts['strings']} text values cleaned"
    + ("" if write else " (dry run)"))


if __name__ == '__main__':
  main()
