#!/usr/bin/env python3
import os
import re
import sys
import json
import glob
import uuid
import html
import yaml
import importlib.util
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime, format_datetime

MANIFEST = '../yaml/bonus-episodes.yaml'
EPISODE_DIR = '../yaml/episodes/'
CHANNEL = '../yaml/daily-source-code.yaml'
PERSONS = '../yaml/persons.yaml'
POSTS = '../json/dsc-posts-mirror.json'
BLOG = '../json/blog-posts.json'
REPO = '../'
AUDIO_DIR = '/media/chrise/work/audio/dsc/DSC/'

MIME_TYPES = {
  '.mp3': 'audio/mpeg',
  '.m4a': 'audio/x-m4a',
  '.m4v': 'video/mp4',
  '.mp4': 'video/mp4',
  '.mov': 'video/quicktime',
}

SUBTITLES = {
  'special': 'Bonus: a special of the Daily Source Code, outside the numbered shows',
  'adam': 'Bonus: Adam Curry, not in the Daily Source Code feed',
  'guest': 'Bonus: Adam Curry on another show',
}


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


audio = load('audio', 'update-episodes-from-audio.py')
timeline = load('timeline', 'locations-timeline.py')


def readJSON(filepath):
  with open(filepath) as fp:
    data = json.load(fp)
  return data if isinstance(data, list) else data.get('posts', [])


def rfcDate(value):
  return format_datetime(value.astimezone(timezone.utc))


def feedItem(path, needle):
  with open(REPO + path, errors='replace') as fp:
    text = fp.read()
  for item in re.findall(r"<item[ >].*?</item>", text, flags=re.S):
    enclosure = re.search(r"<enclosure[^>]*url=[\"']([^\"']+)[\"'][^>]*>", item)
    if enclosure is None or needle not in enclosure.group(1):
      continue
    def tag(name):
      found = re.search(rf"<{name}[^>]*>(.*?)</{name}>", item, flags=re.S)
      if found is None:
        return None
      value = found.group(1).strip()
      cdata = re.fullmatch(r"<!\[CDATA\[(.*)\]\]>", value, flags=re.S)
      return cdata.group(1).strip() if cdata else html.unescape(value)
    length = re.search(r"length=[\"'](\d+)[\"']", enclosure.group(0))
    return {
      'title': html.unescape(tag('title') or '').strip(),
      'pubDate': tag('pubDate'),
      'link': tag('link'),
      'guid': tag('guid'),
      'description': tag('content:encoded') or tag('description'),
      'subtitle': tag('itunes:subtitle'),
      'url': html.unescape(enclosure.group(1)),
      'length': int(length.group(1)) if length else None,
    }
  sys.exit(f"{path}: no item with an enclosure like {needle}")


def origin(entry, posts, blog):
  src = entry.get('origin') or {}
  if 'post' in src:
    post = next((p for p in posts if p.get('permalink') == src['post']), None)
    if post is None:
      sys.exit(f"{entry['id']}: post {src['post']} not found")
    return {
      'title': post.get('title'),
      'pubDate': post.get('pubDate'),
      'link': post['permalink'],
      'guid': post['permalink'],
      'description': post.get('description'),
      'url': (post.get('enclosure') or {}).get('url'),
      'length': (post.get('enclosure') or {}).get('length'),
    }
  if 'blog' in src:
    post = next((p for p in blog if p.get('permalink') == src['blog']), None)
    if post is None:
      sys.exit(f"{entry['id']}: blog post {src['blog']} not found")
    when = f"{post['date']} {post.get('time') or '12:00:00 +0000'}"
    return {
      'title': post.get('title'),
      'pubDate': datetime.strptime(when, '%Y-%m-%d %H:%M:%S %z'),
      'link': post['permalink'],
      'guid': post['permalink'],
      'description': post.get('text'),
    }
  if 'feed' in src:
    return feedItem(src['feed'], src['enclosure'])
  return {}


def personTags(entry, persons):
  tags = []
  people = {p['name']: p for p in persons}
  adam = people['Adam Curry']
  host = {'person': adam['name'], 'href': adam.get('href'), 'img': adam.get('img'),
    'group': adam.get('group', 'cast'), 'role': entry.get('adam', 'host')}
  tags.append(host)
  for name in entry.get('people') or []:
    person = people.get(name)
    if person is None:
      sys.exit(f"{entry['id']}: {name} is not in persons.yaml")
    role = next((e.get('role') for e in person.get('episodes') or []
      if str(e.get('episode')) == f"bonus-{entry['id']}"), person.get('role', 'guest'))
    tags.append({'person': name, 'href': person.get('href'), 'img': person.get('img'),
      'group': person.get('group', 'cast'), 'role': role})
  return tags


def sourcePath(source):
  return REPO + source if source.startswith('mp3/') else AUDIO_DIR + source


def build(entry, posts, blog, persons):
  facts = origin(entry, posts, blog)
  for key in ('title', 'description', 'url', 'link', 'subtitle'):
    if entry.get(key) is not None:
      facts[key] = entry[key]
  when = facts.get('pubDate')
  if isinstance(when, str):
    when = parsedate_to_datetime(when)
  if when is None or when.tzinfo is None:
    if entry.get('date') is None:
      sys.exit(f"{entry['id']}: no date")
    day = entry['date'] if not isinstance(entry['date'], str) else datetime.strptime(entry['date'], '%Y-%m-%d').date()
    when = datetime(day.year, day.month, day.day, 12, 0, 0, tzinfo=timezone.utc)
  if not facts.get('title'):
    sys.exit(f"{entry['id']}: no title")

  path = sourcePath(entry['source'])
  info = audio.probe(path)
  size = int(info['format']['size'])
  duration = audio.decodeDuration(path) or float(info['format']['duration'])
  bitrate = int(info['format'].get('bit_rate') or 0) or None
  ext = os.path.splitext(entry['source'])[1].lower()
  mime = MIME_TYPES[ext]
  url = facts.get('url')
  guid = facts.get('guid') or facts.get('link') or url or f"bonus-{entry['id']}"
  description = audio.trimLines(facts.get('description') or facts['title'])
  subtitle = entry.get('subtitle') or SUBTITLES[entry['kind']]
  author = entry.get('author') or 'Adam Curry'

  return {
    'episode': None,
    'title': facts['title'],
    'link': facts.get('link'),
    'pubDate': rfcDate(when),
    'category': 'podcast',
    'description': description,
    'author': author,
    'language': 'en-us',
    'comments': None,
    'guid': {'isPermaLink': False, 'link': guid},
    'enclosure': {'url': url, 'length': facts.get('length') or size, 'type': mime},
    'itunes': {
      'author': author,
      'title': facts['title'],
      'subtitle': subtitle,
      'summary': description,
      'explicit': True,
      'keywords': 'adam,curry,daily,source,code,delta,sierra,charlie,dsc',
      'duration': int(round(duration)),
      'season': None,
      'episode': None,
      'episodeType': 'bonus',
      'image': None,
    },
    'podcast': {
      'episode': None,
      'season': None,
      'license': None,
      'guid': str(uuid.uuid3(uuid.NAMESPACE_URL, guid)),
      'location': None,
      'person': personTags(entry, persons),
      'images': None,
      'chapters': None,
      'transcript': None,
      'alternateEnclosure': [{
        'type': mime,
        'length': size,
        'bitrate': bitrate,
        'default': True,
        'title': f"DSC Bonus {entry['id'][:10]}",
        'source': {'uri': url},
      }],
    },
    'fileinfo': {
      'filename': os.path.basename(entry['source']),
      'size': size,
      'duration': int(round(duration)),
      'bitrate': bitrate,
      'source': entry['source'],
      'origin_url': url,
    },
    'bonus': {
      'id': entry['id'],
      'kind': entry['kind'],
      'basis': entry.get('basis') or next(iter((entry.get('origin') or {}).values()), None),
    },
  }


def numberedDates():
  rows = []
  for path in sorted(glob.glob(f"{EPISODE_DIR}[0-9][0-9][0-9].yaml")):
    with open(path) as fp:
      ep = yaml.safe_load(fp)
    rows.append((os.path.basename(path), timeline.showDate(ep)))
  return rows


def layout(bonus):
  order = []
  pending = sorted(bonus, key=lambda b: (b[1], b[2]))
  for name, day in numberedDates():
    while pending and pending[0][1] < day:
      order.append(pending.pop(0)[0])
    order.append(name)
  order.extend(b[0] for b in pending)
  return order


def writeList(order):
  with open(CHANNEL) as fp:
    text = fp.read()
  head, found, _ = text.partition('\nepisodes:\n')
  if not found:
    sys.exit(f"{CHANNEL}: no episodes list")
  with open(CHANNEL, 'w') as fp:
    fp.write(head + '\nepisodes:\n' + ''.join(f"- {name}\n" for name in order))


def main():
  write = '--write' in sys.argv
  with open(MANIFEST) as fp:
    manifest = yaml.safe_load(fp)['bonus']
  with open(PERSONS) as fp:
    persons = yaml.safe_load(fp)['persons']
  posts, blog = readJSON(POSTS), readJSON(BLOG)
  ids = [e['id'] for e in manifest]
  clashes = sorted({i for i in ids if ids.count(i) > 1})
  if clashes:
    sys.exit(f"duplicate ids: {clashes}")

  rows = []
  for entry in manifest:
    ep = build(entry, posts, blog, persons)
    name = f"bonus-{entry['id']}.yaml"
    day = entry['id'][:10]
    published = parsedate_to_datetime(ep['pubDate']).astimezone(timezone.utc).replace(tzinfo=None)
    if day != published.strftime('%Y-%m-%d'):
      print(f"note: {name} id date differs from pubDate {ep['pubDate']}")
    rows.append((name, day, published))
    print(f"{name}: {ep['title']} | {ep['pubDate']} | {ep['enclosure']['type']} {ep['fileinfo']['duration']} s")
    if write:
      audio.writeYAML(EPISODE_DIR + name, ep)

  stale = sorted(set(os.path.basename(p) for p in glob.glob(f"{EPISODE_DIR}bonus-*.yaml")) - {r[0] for r in rows})
  for name in stale:
    print(f"stale (not in the manifest): {name}")

  if '--list' in sys.argv:
    order = layout(rows)
    print(f"episode list: {len(order)} ({len(order) - len(rows)} numbered, {len(rows)} bonus)")
    if write:
      writeList(order)


if __name__ == '__main__':
  main()
