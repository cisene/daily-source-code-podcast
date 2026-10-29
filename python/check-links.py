#!/usr/bin/env python3
import os
import re
import sys
import glob
import yaml
import importlib.util

CHANNEL = '../yaml/daily-source-code.yaml'
UPLOAD = '../yaml/upload.yaml'
RELEASE = '../yaml/release-audio.yaml'
EPISODE_DIR = '../yaml/episodes/'
ARTWORK_DIR = '../artwork/'
URL_SAFE = re.compile(r"^[A-Za-z0-9._/-]+$")


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


def strings(data):
  if isinstance(data, dict):
    for v in data.values():
      yield from strings(v)
  elif isinstance(data, list):
    for v in data:
      yield from strings(v)
  elif isinstance(data, str):
    yield data


def planned(stage):
  with open(RELEASE) as fp:
    rows = yaml.safe_load(fp)['audio']
  files = {os.path.join(stage.mediaFolder(r['release']), r['release']) for r in rows}
  for base, ext, folder in ((stage.SRT_DIR, '.srt', 'srt'), (stage.VTT_DIR, '.vtt', 'vtt')):
    files |= {rel for _, rel in stage.transcriptPairs(rows, base, ext, folder)}
  files |= {'chapters/' + os.path.basename(p) for p in glob.glob(f"{stage.CHAPTERS_DIR}*/*.json")}
  files |= {'opml/' + os.path.basename(p) for p in glob.glob(f"{stage.SHOWNOTES_DIR}*/*.opml")}
  files |= {'artwork/' + os.path.basename(p) for p in glob.glob(f"{ARTWORK_DIR}*.png")}
  files.add('rss.xml')
  return files


def main():
  stage = load('stage', 'stage-release.py')
  with open(CHANNEL) as fp:
    channel = yaml.safe_load(fp)
  feed = channel['feed']
  base = str(feed['base_url']).rstrip('/')
  host = re.sub(r"^https?://", '', base)
  prefixes = [base + '/', base.replace('https://', 'http://') + '/']
  for kind in ('audio_url', 'video_url'):
    prefixes.append(str(feed[kind]).rstrip('/').rsplit(host, 1)[0] + host + '/')
  prefixes = sorted(set(prefixes), key=len, reverse=True)

  files = planned(stage)
  linked, broken, unsafe, sizes = {}, [], [], []
  with open(UPLOAD) as fp:
    stage_dir = yaml.safe_load(fp).get('stage')
  staged = bool(stage_dir) and os.path.isdir(stage_dir)

  def media(where, url, length):
    for prefix in prefixes:
      if staged and url and url.startswith(prefix):
        path = os.path.join(stage_dir, url[len(prefix):])
        if not os.path.exists(path):
          sizes.append(f"{where}: {url} not staged")
        elif str(os.path.getsize(path)) != str(length):
          sizes.append(f"{where}: {url} length {length}, staged {os.path.getsize(path)}")
        return

  def check(where, value):
    value = value.replace('__BASE_URL__', base)
    for prefix in prefixes:
      if value.startswith(prefix):
        path = value[len(prefix):].split('#')[0].split('?')[0]
        if path == '':
          return
        linked.setdefault(path, where)
        if not URL_SAFE.match(path):
          unsafe.append(f"{where}: {value}")
        if path not in files:
          broken.append(f"{where}: {value}")
        return

  for value in strings(channel):
    if value not in (feed['base_url'], feed['audio_url'], feed['video_url']):
      check('channel', value)
  for path in sorted(glob.glob(f"{EPISODE_DIR}*.yaml")):
    with open(path) as fp:
      ep = yaml.safe_load(fp)
    for value in strings({k: v for k, v in ep.items() if k != 'fileinfo'}):
      check(os.path.basename(path), value)
    enc = ep.get('enclosure') or {}
    media(os.path.basename(path), enc.get('url'), enc.get('length'))
    for alt in (ep.get('podcast') or {}).get('alternateEnclosure') or []:
      srcs = alt.get('source') or []
      for src in [srcs] if isinstance(srcs, dict) else srcs:
        media(os.path.basename(path), src.get('uri'), alt.get('length'))

  for line in broken:
    print(f"broken: {line}")
  for line in unsafe:
    print(f"not url-safe: {line}")
  for line in sizes:
    print(f"length: {line}")
  unlinked = sorted(files - set(linked))
  folders = {}
  for path in unlinked:
    folders.setdefault(path.split('/')[0] if '/' in path else path, []).append(path)
  for folder, paths in sorted(folders.items()):
    print(f"not linked: {folder}: {len(paths)}" + (f" ({', '.join(paths[:5])}{' ...' if len(paths) > 5 else ''})" if folder != 'opml' else ''))
  print(f"{len(linked)} distinct links to our host, {len(broken)} broken, {len(unsafe)} not url-safe; {len(files)} files planned; "
    + (f"{len(sizes)} lengths off the stage" if staged else "lengths not checked (no stage yet)"))
  if broken or unsafe or sizes:
    sys.exit(1)


if __name__ == '__main__':
  main()
