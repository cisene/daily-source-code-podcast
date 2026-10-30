#!/usr/bin/env python3
import os
import sys
import difflib
import tempfile
import urllib.request
import yaml

CHANNEL = '../yaml/daily-source-code.yaml'
UPLOAD = '../yaml/upload.yaml'
USER_AGENT = 'daily-source-code-podcast (https://github.com/cisene/daily-source-code-podcast)'
IGNORE = ('<lastBuildDate>',)


def main():
  with open(CHANNEL) as fp:
    feed = yaml.safe_load(fp)['feed']
  url = f"{str(feed['base_url']).rstrip('/')}/{feed['filename']}"
  with open(UPLOAD) as fp:
    stage = yaml.safe_load(fp)['stage']
  staged_path = os.path.join(stage, 'feed', feed['filename'])

  request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Cache-Control': 'no-cache'})
  with urllib.request.urlopen(request, timeout=60) as response:
    live = response.read()
  live_path = os.path.join(tempfile.gettempdir(), 'dsc-live-' + feed['filename'])
  with open(live_path, 'wb') as fp:
    fp.write(live)

  with open(staged_path, 'rb') as fp:
    staged = fp.read()

  print(f"live:   {url} ({len(live)} bytes), saved to {live_path}")
  print(f"staged: {staged_path} ({len(staged)} bytes)")
  if live == staged:
    print("identical: no changes on the site, safe to render and push")
    return

  diff = [line for line in difflib.unified_diff(
            staged.decode('utf-8').splitlines(), live.decode('utf-8').splitlines(),
            'staged', 'live', n=0, lineterm='')
          if line[:1] in '+-' and not line.startswith(('---', '+++'))]
  changes = [line for line in diff if not any(tag in line for tag in IGNORE)]
  if not changes:
    print("only lastBuildDate differs: safe to render and push")
    return
  print(f"CHANGED ON THE SITE: {len(changes)} lines differ from the last upload")
  for line in changes[:200]:
    print(line)
  if len(changes) > 200:
    print(f"... {len(changes) - 200} more, see the full live copy at {live_path}")
  print("Mirror these into the yaml first, render, then compare again before pushing.")
  sys.exit(1)


if __name__ == '__main__':
  main()
