#!/usr/bin/env python3
import os
import re
import sys
import glob
import yaml
import importlib.util

EPISODE_DIR = '../yaml/episodes/'
OUT = '../yaml/release-audio.yaml'

DISAMBIGUATE = {
  '010': 'test',
  '032': 'Trade-Secrets',
  '051': 'ipodder',
  '052': 'to-adam-from-dawn',
  '172': 'RVZR',
}


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


timeline = load('timeline', 'locations-timeline.py')


def main():
  rows, problems = [], []
  for path in sorted(glob.glob(f"{EPISODE_DIR}[0-9][0-9][0-9].yaml")):
    episode = os.path.basename(path)[:3]
    with open(path) as fp:
      ep = yaml.safe_load(fp)
    source = str(ep['fileinfo']['source'])
    date = timeline.showDate(ep)
    ext = os.path.splitext(source)[1].lower()
    name = f"DSC-{date}" + (f"-{DISAMBIGUATE[episode]}" if episode in DISAMBIGUATE else '')
    if not re.fullmatch(r"DSC-\d{4}-\d\d-\d\d(-[A-Za-z0-9-]+)?", name):
      problems.append(f"{episode}: {source} ({date}) has no release name")
    rows.append({'episode': episode, 'date': date, 'source': source,
      'release': name + ext, 'size': ep['fileinfo'].get('size')})
  for path in sorted(glob.glob(f"{EPISODE_DIR}bonus-*.yaml")):
    with open(path) as fp:
      ep = yaml.safe_load(fp)
    source = str(ep['fileinfo']['source'])
    name = f"DSC-{ep['bonus']['id']}"
    if not re.fullmatch(r"DSC-\d{4}-\d\d-\d\d(-[A-Za-z0-9-]+)?", name):
      problems.append(f"{os.path.basename(path)}: {source} has no release name")
    rows.append({'episode': os.path.basename(path)[:-5], 'date': ep['bonus']['id'][:10], 'source': source,
      'release': name + os.path.splitext(source)[1].lower(), 'size': ep['fileinfo'].get('size')})
  names = [r['release'] for r in rows]
  clashes = sorted({n for n in names if names.count(n) > 1})
  if problems or clashes:
    print('\n'.join(problems + [f"clash: {n}" for n in clashes]))
    sys.exit(1)
  with open(OUT, 'w') as fp:
    fp.write("# Episode audio for the re-release: source (archive path, or mp3/ in the repo),\n"
      "# release name (DSC-YYYY-MM-DD.ext, a text only for a second episode of the day;\n# served flat under /audio/), size of the\n"
      "# source in bytes. Written by python/release-audio-names.py.\n")
    yaml.safe_dump({'audio': rows}, fp, sort_keys=False, allow_unicode=True, width=1000)
  renamed = [r for r in rows if r['release'] != os.path.basename(r['source'])]
  print(f"{len(rows)} episodes, {len(renamed)} renamed, no clashes")


if __name__ == '__main__':
  main()
