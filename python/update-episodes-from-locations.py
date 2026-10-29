#!/usr/bin/env python3
import os
import sys
import glob
import yaml
import importlib.util

EPISODE_DIR = '../yaml/episodes/'
LOCATIONS = '../yaml/locations.yaml'
PERSONS = '../yaml/persons.yaml'

WRITE = '--write' in sys.argv

COUNTRY_CODES = {'UK': 'GB'}
OSM_TYPES = {'node': 'N', 'way': 'W', 'relation': 'R'}


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


audio = load('audio', 'update-episodes-from-audio.py')
timeline = load('timeline', 'locations-timeline.py')


def readPeriods():
  with open(LOCATIONS) as fp:
    locations = yaml.safe_load(fp)['locations']
  byhand, found = [], []
  for entry in locations:
    for p in entry.get('recorded') or []:
      byhand.append((str(p['from']), str(p.get('to') or p['from']), entry))
    for p in entry.get('at') or []:
      found.append((str(p['from']), str(p.get('to') or p['from']), entry))
  return byhand + found


def locationOf(periods, date):
  for a, b, entry in periods:
    if a <= date <= b:
      return entry
  return None


def locationTag(entry):
  placename = entry.get('placename')
  country = None
  if placename and ', ' in placename:
    cc = placename.rsplit(', ', 1)[1]
    country = COUNTRY_CODES.get(cc, cc)
  if entry['type'] == 'place':
    name = entry['location'] if entry.get('precision') == 'country' else placename
  else:
    name = ', '.join(v for v in [entry['location'], placename] if v)
  geo = None
  if entry.get('latitude') != None and entry.get('longitude') != None:
    geo = f"geo:{entry['latitude']},{entry['longitude']}"
  osm = None
  if entry.get('osm'):
    kind, _, ident = str(entry['osm']).partition('/')
    osm = f"{OSM_TYPES[kind]}{ident}" if kind in OSM_TYPES else None
  return {'rel': 'creator', 'geo': geo, 'osm': osm, 'country': country, 'name': name}


def personTags(persons, episode):
  tags = []
  for p in persons:
    roles = [e['role'] for e in p.get('episodes') or [] if str(e['episode']) == episode]
    if 'episodes' in p and len(roles) == 0:
      continue
    tags.append({
      'person': p['name'],
      'href': p.get('href'),
      'img': p.get('img'),
      'group': p.get('group'),
      'role': roles[0] if roles else p.get('role'),
    })
  return tags


def main():
  periods = readPeriods()
  with open(PERSONS) as fp:
    persons = yaml.safe_load(fp)['persons']

  log, nolocation, written = [], [], 0
  for path in sorted(glob.glob(f"{EPISODE_DIR}[0-9][0-9][0-9].yaml")):
    episode = os.path.basename(path)[:3]
    ep = audio.readYAML(path)
    if not isinstance(ep, dict) or not isinstance(ep.get('podcast'), dict):
      log.append(f"{episode}: no podcast block, skipped")
      continue
    date = timeline.showDate(ep)
    entry = locationOf(periods, date) if date else None
    if entry == None:
      nolocation.append(f"{episode} ({date})")
      location = {'rel': 'creator', 'geo': None, 'osm': None, 'country': None, 'name': None}
    else:
      location = locationTag(entry)
    people = personTags(persons, episode)
    if ep['podcast'].get('location') != location or ep['podcast'].get('person') != people:
      ep['podcast']['location'] = location
      ep['podcast']['person'] = people
      written += 1
      if WRITE:
        audio.writeYAML(path, ep)

  print('\n'.join(log))
  print(f"{written} episodes changed" + ('' if WRITE else ' (dry run, --write to save)'))
  if nolocation:
    print('no location:', ', '.join(nolocation))


if __name__ == '__main__':
  main()
