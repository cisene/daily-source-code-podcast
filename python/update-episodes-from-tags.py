#!/usr/bin/env python3
import os
import sys
import json
import types
import datetime
import subprocess
import importlib.util

EPISODE_DIR = '../yaml/episodes/'
ARCHIVE_DIR = '/media/chrise/work/audio/dsc/DSC/'
TAGS_FILE = '../json/dsc-archive-tag-enclosures.json'
EPISODE_LAST = 867


def loadScript(name, filename, stubs=[]):
  for stub in stubs:
    sys.modules.setdefault(stub, types.ModuleType(stub))
  spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


audio = loadScript('audio', 'update-episodes-from-audio.py')
posts = loadScript('posts', 'update-episodes-from-posts.py', stubs=['feedparser'])


def fileTags(path):
  r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags', '-of', 'json', path], capture_output=True, text=True)
  return {k.upper(): v for k, v in (json.loads(r.stdout or '{}').get('format', {}).get('tags') or {}).items()}


def main():
  dry_run = '--dry-run' in sys.argv
  with open(TAGS_FILE) as fp:
    tagged = json.load(fp)

  log = []
  for n in range(1, EPISODE_LAST + 1):
    path = f"{EPISODE_DIR}{n:03}.yaml"
    ep = audio.readYAML(path)
    if not isinstance(ep, dict) or not isinstance(ep.get('fileinfo'), dict) or posts.hasScheme(audio.get(ep, 'enclosure', 'url')):
      continue
    source = audio.get(ep, 'fileinfo', 'source')
    urls = (tagged.get(source) or {}).get('urls', [])
    if len(urls) != 1:
      continue
    changes = []
    old_url = audio.get(ep, 'enclosure', 'url')
    ep['enclosure']['url'] = urls[0]
    for ae in audio.alternateEnclosures(ep):
      if isinstance(ae.get('source'), dict) and os.path.basename(str(old_url)) in audio.sourceBasenames(ae) and not posts.hasScheme(ae['source'].get('uri')):
        ae['source']['uri'] = urls[0]
    changes.append('enclosure url')

    tags = fileTags(ARCHIVE_DIR + source)
    tgid = tags.get('TGID') or tags.get('TID')
    if tgid and tgid.startswith('http://radio.weblogs.com/'):
      if posts.isPlaceholder(ep.get('link'), '#daily-source-code-episode-web'):
        ep['link'] = tgid
        changes.append('link')
      if isinstance(ep.get('guid'), dict) and posts.isPlaceholder(ep['guid'].get('link'), '#daily-source-code-episode-guid'):
        ep['guid']['link'] = tgid
        ep['guid']['isPermaLink'] = False
        changes.append('guid')

    released = tags.get('TDRL') or tags.get('TDR')
    if released and 'T' in released and posts.isDateOnly(ep.get('pubDate')):
      when = datetime.datetime.fromisoformat(released.replace('Z', '+00:00'))
      old_pubDate = ep['pubDate']
      ep['pubDate'] = when.strftime('%a %b %d %H:%M:%S %Y %z')
      for ns in ['itunes', 'podcast']:
        if isinstance(ep.get(ns), dict) and 'pubDate' in ep[ns] and (posts.isDateOnly(ep[ns]['pubDate']) or ep[ns]['pubDate'] == old_pubDate):
          ep[ns]['pubDate'] = ep['pubDate']
      changes.append('pubDate')

    log.append(f"{n:03}: {', '.join(changes)} from the tags of {source}")
    if not dry_run:
      audio.writeYAML(path, ep)

  print("\n".join(log))
  print(f"Episodes {'to update' if dry_run else 'updated'}: {len(log)}")


if __name__ == '__main__':
  main()
