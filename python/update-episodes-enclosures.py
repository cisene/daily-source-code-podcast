#!/usr/bin/env python3
import os
import re
import sys
import yaml
import importlib.util

CHANNEL = '../yaml/daily-source-code.yaml'
RELEASE = '../yaml/release-audio.yaml'
UPLOAD = '../yaml/upload.yaml'
EPISODE_DIR = '../yaml/episodes/'

LANGUAGES = {
  '172': 'nl',
  'bonus-2005-05-17-RVZR': 'nl',
}

URL_SAFE = re.compile(r"^https://[A-Za-z0-9.-]+(/[A-Za-z0-9._-]+)+$")

MIME_TYPES = {
  '.mp3': 'audio/mpeg',
  '.m4a': 'audio/x-m4a',
  '.m4v': 'video/mp4',
  '.mp4': 'video/mp4',
  '.mov': 'video/quicktime',
}


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


audio = load('audio', 'update-episodes-from-audio.py')


def shortTitle(ep, row):
  if ep.get('episode') not in (None, ''):
    return f"DSC #{int(ep['episode'])}"
  return f"DSC Bonus {row['date']}"


def main():
  write = '--write' in sys.argv
  with open(CHANNEL) as fp:
    feed = yaml.safe_load(fp)['feed']
  prefixes = {}
  for kind in ('audio', 'video'):
    prefixes[kind] = str(feed[f"{kind}_url"]).rstrip('/') + '/'
  with open(RELEASE) as fp:
    rows = yaml.safe_load(fp)['audio']
  with open(UPLOAD) as fp:
    stage = yaml.safe_load(fp).get('stage')

  changed, dropped, problems, staged_count = 0, [], [], 0
  for row in rows:
    name = row['episode']
    path = f"{EPISODE_DIR}{name}.yaml"
    ext = os.path.splitext(row['release'])[1]
    mime = MIME_TYPES[ext]
    url = prefixes[mime.split('/')[0]] + row['release']
    if not URL_SAFE.match(url):
      problems.append(f"{name}: not url-safe: {url}")
      continue
    ep = audio.readYAML(path)
    if ep is None:
      problems.append(f"{name}: no yaml")
      continue
    info = ep.setdefault('fileinfo', {})
    old = (ep.get('enclosure') or {}).get('url')
    if old and old != url and not info.get('origin_url'):
      info['origin_url'] = old
    staged = os.path.join(stage, 'audio', row['release']) if stage else None
    if staged and os.path.exists(staged):
      size = os.path.getsize(staged)
      staged_count += 1
    else:
      size = row.get('size') or info.get('size')
    alternates = (ep.get('podcast') or {}).get('alternateEnclosure') or []
    for alt in alternates[1:]:
      dropped.append(f"{name}: {alt.get('type')} {(alt.get('source') or {}).get('uri')}")
    before = (ep.get('enclosure'), alternates)
    ep['enclosure'] = {'url': url, 'length': size, 'type': mime}
    ep['podcast']['alternateEnclosure'] = [{
      'type': mime,
      'length': size,
      'bitrate': info.get('bitrate'),
      'lang': LANGUAGES.get(name),
      'default': True,
      'title': shortTitle(ep, row),
      'source': {'uri': url},
    }]
    if before != (ep['enclosure'], ep['podcast']['alternateEnclosure']):
      changed += 1
      if write:
        audio.writeYAML(path, ep)

  for line in dropped:
    print(f"dropped alternate: {line}")
  for line in problems:
    print(line)
  print(f"{len(rows)} episodes, {staged_count} lengths from the stage, {changed} changed" + ("" if write else " (dry run)"))
  if problems:
    sys.exit(1)


if __name__ == '__main__':
  main()
