#!/usr/bin/env python3
import os
import sys
import glob
import yaml
import importlib.util

CHANNEL = '../yaml/daily-source-code.yaml'
RELEASE = '../yaml/release-audio.yaml'
EPISODE_DIR = '../yaml/episodes/'
CHAPTERS_DIR = '../chapters/'
EPISODE_IMAGE = 'artwork/episode-300x300.png'
LANGUAGE = 'en'
IMAGE_ALT = "Daily Source Code: the words DAILY SOURCE CODE on three tilted bands, white on navy and navy on white (the show's first logo, 2004, reconstructed)"


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


audio = load('audio', 'update-episodes-from-audio.py')
stage = load('stage', 'stage-release.py')


def transcripts(rows):
  index = stage.transcriptIndex(rows)
  found = {}
  for base, ext in ((stage.SRT_DIR, '.srt'), (stage.VTT_DIR, '.vtt')):
    for path in glob.glob(f"{base}*/*{ext}"):
      release = index.get(os.path.splitext(os.path.basename(path))[0])
      if release:
        found.setdefault(release, set()).add(ext)
  return found


def main():
  write = '--write' in sys.argv
  with open(CHANNEL) as fp:
    base = str(yaml.safe_load(fp)['feed']['base_url']).rstrip('/')
  with open(RELEASE) as fp:
    rows = yaml.safe_load(fp)['audio']
  have = transcripts(rows)
  chapters = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(f"{CHAPTERS_DIR}*/*.json")}
  image = f"{base}/{EPISODE_IMAGE}"

  changed = counts = 0
  tally = {'transcript': 0, 'srt only': 0, 'chapters': 0}
  for row in rows:
    path = f"{EPISODE_DIR}{row['episode']}.yaml"
    ep = audio.readYAML(path)
    stem = os.path.splitext(row['release'])[0]
    before = yaml.safe_dump(ep)
    if 'originalLink' not in ep:
      ordered = {}
      for key, value in ep.items():
        ordered[key] = value
        if key == 'link':
          ordered['originalLink'] = value
      ep = ordered
    ep['link'] = f"{base}/episodes/{stem}.html"
    podcast = ep['podcast']

    exts = have.get(stem, set())
    links = []
    if '.vtt' in exts:
      links.append({'url': f"{base}/vtt/{stem}.vtt", 'type': 'text/vtt', 'language': LANGUAGE, 'rel': 'captions'})
    if '.srt' in exts:
      links.append({'url': f"{base}/srt/{stem}.srt", 'type': 'application/x-subrip', 'language': LANGUAGE, 'rel': 'captions'})
    podcast['transcript'] = links or None
    if links:
      tally['transcript'] += 1
      if '.vtt' not in exts:
        tally['srt only'] += 1

    if stem in chapters:
      podcast['chapters'] = [{'url': f"{base}/chapters/{stem}.json", 'type': 'application/json+chapters'}]
      tally['chapters'] += 1
    else:
      podcast['chapters'] = None

    ep['itunes']['image'] = {'href': image}
    podcast.pop('images', None)
    podcast['image'] = [{'href': image, 'alt': IMAGE_ALT, 'aspect-ratio': '1/1', 'width': 300,
      'height': 300, 'type': 'image/png', 'purpose': 'artwork'}]

    podcast.pop('socialInteract', None)

    if yaml.safe_dump(ep) != before:
      changed += 1
      if write:
        audio.writeYAML(path, ep)
    counts += 1

  print(f"{counts} episodes: {tally['transcript']} with transcripts ({tally['srt only']} srt only, no vtt yet), "
    f"{tally['chapters']} with chapters; {changed} changed" + ("" if write else " (dry run)"))


if __name__ == '__main__':
  main()
