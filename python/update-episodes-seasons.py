#!/usr/bin/env python3
import sys
import yaml
import importlib.util

RELEASE = '../yaml/release-audio.yaml'
EPISODE_DIR = '../yaml/episodes/'
FIRST_YEAR = 2004


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


audio = load('audio', 'update-episodes-from-audio.py')


def main():
  write = '--write' in sys.argv
  years = '--years' in sys.argv
  with open(RELEASE) as fp:
    rows = yaml.safe_load(fp)['audio']

  changed = 0
  seasons = {}
  for row in rows:
    path = f"{EPISODE_DIR}{row['episode']}.yaml"
    ep = audio.readYAML(path)
    year = int(str(row['date'])[:4])
    number = str(year) if years else str(year - FIRST_YEAR + 1)
    seasons[year] = seasons.get(year, 0) + 1
    before = yaml.safe_dump(ep)
    ep['itunes']['season'] = number
    ep['podcast']['season'] = {'number': number, 'name': None if years else str(year)}
    if yaml.safe_dump(ep) != before:
      changed += 1
      if write:
        audio.writeYAML(path, ep)

  for year in sorted(seasons):
    print(f"season {year if years else year - FIRST_YEAR + 1} ({year}): {seasons[year]} episodes")
  print(f"{len(rows)} episodes, {changed} changed" + ("" if write else " (dry run)"))


if __name__ == '__main__':
  main()
