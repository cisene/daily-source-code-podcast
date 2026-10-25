#!/usr/bin/env python3
# List the published enclosure urls named in the tags of the archive files.
#
# From 2006 on the archive files carry the original post in their tags (TDES,
# comment) with its "Direct link to the show", and often the item guid (TGID).
# That names the feed item the file was published as, whatever date is in the
# archive file name. Writes json/dsc-archive-tag-enclosures.json:
#   { "2007/DSC-2007-12-04.mp3": { "title": ..., "urls": [...] }, ... }
#
# The archive is only read (ffprobe).

import os
import re
import sys
import json
import subprocess

ARCHIVE_DIR = '/media/chrise/work/audio/dsc/DSC'
OUTPUT_FILE = '../json/dsc-archive-tag-enclosures.json'
MEDIA = re.compile(r"(?i)\.(mp3|m4a|mp4|m4v|mov)$")
URL = re.compile(r"https?://[^\s\"'<>]+?\.(?:mp3|m4a|mp4|m4v|mov)\b")


def readTags(path):
  result = subprocess.run(['ffprobe', '-v', 'quiet', '-of', 'json', '-show_entries', 'format_tags', path], capture_output=True)
  try:
    return json.loads(result.stdout.decode('utf-8', errors='replace')).get('format', {}).get('tags', {})
  except ValueError:
    return {}


def main():
  archive = sys.argv[1] if len(sys.argv) > 1 else ARCHIVE_DIR
  files = {}
  for root, dirs, names in os.walk(archive):
    dirs.sort()
    for name in sorted(names):
      if not MEDIA.search(name):
        continue
      path = os.path.join(root, name)
      tags = readTags(path)
      urls = []
      for value in tags.values():
        for url in URL.findall(str(value)):
          if url not in urls:
            urls.append(url)
      if len(urls) > 0:
        files[os.path.relpath(path, archive)] = {'title': tags.get('title'), 'urls': urls}

  with open(OUTPUT_FILE, 'w') as fp:
    json.dump(files, fp, indent=1, sort_keys=True, ensure_ascii=False)
  print(f"{len(files)} archive files name published urls")


if __name__ == '__main__':
  main()
