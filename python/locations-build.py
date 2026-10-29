#!/usr/bin/env python3
import os
import re
import sys
import json
import math
import time
import yaml
import urllib.parse
import urllib.request
import importlib.util

spec = importlib.util.spec_from_file_location('geocode', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locations-geocode.py'))
geocode = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geocode)

LOCATIONS = '../yaml/locations.yaml'
GEONAMES_DIR = os.path.expanduser('~/.cache/geonames/')
CACHE = os.path.expanduser('~/.cache/dsc-locations/lookups.json')
OFFLINE = False
USER_AGENT = 'daily-source-code-podcast locations (https://github.com/cisene/daily-source-code-podcast)'
PACE = 12

FIELDS = ['location', 'type', 'origin', 'aliases', 'placename', 'latitude', 'longitude', 'altitude', 'precision', 'query', 'osm', 'geonames', 'notes', 'recorded', 'at']
SECTIONS = [('residence', 'Residences'), ('vehicle', 'Vehicles: cars and aircraft (no fixed place)'), ('venue', 'Venues'), ('place', 'Places: towns, regions, countries'), ('unresolved', 'Said as the recording place, not resolved: to resolve by hand')]
HEADER = """# Recording locations of the Daily Source Code: where Adam lived and
# recorded, and the venues, vehicles and towns he recorded from.
# Written by python/locations-build.py; hand edits to curated entries are kept.
#
# location   name as used in the show (other names in aliases)
# type       residence, vehicle, venue, place (town, region, country), or
#            unresolved (said as the recording place, not resolved yet)
# origin     curated (checked by hand, kept) or generated (a show says it was
#            recorded there, found by locations-timeline.py; rebuilt on
#            every run, set to curated to keep a hand edit)
# placename  "Town, CC"
# latitude, longitude  WGS-84 degrees; null = not resolved yet (by hand, or ask Adam)
# altitude   metres above sea level (GeoNames elevation / DEM, or SRTM 30 m), null = unknown
# precision  what the coordinates point at: building, street, area, town, region, country
# query      Nominatim search used for the lookup
# osm, geonames  ids of the place the coordinates came from (osm as type/id)
# notes      what the sources say, with the file it is from
# recorded   periods set by hand (from/to): shows in them are taken to be
#            recorded here, whatever the transcript says; kept on every run
# at         periods the shows were recorded here (locations-timeline.py): from/to
#            show dates, shows in the period, how many of them say so (stated),
#            and how many say only the country or continent, which fits
#            (confirmed); the other shows are assumed to be at the same place
"""


def loadCache():
  try:
    with open(CACHE) as fp:
      return json.load(fp)
  except (OSError, ValueError):
    return {}


def saveCache(cache):
  os.makedirs(os.path.dirname(CACHE), exist_ok=True)
  with open(CACHE, 'w') as fp:
    json.dump(cache, fp, indent=1, ensure_ascii=False)


def fetch(url):
  request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
  with urllib.request.urlopen(request, timeout=60) as r:
    return json.loads(r.read().decode('utf-8'))


def nominatim(query, cache):
  key = 'nominatim:' + query
  if key not in cache:
    if OFFLINE:
      return None
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode({'q': query, 'format': 'jsonv2', 'limit': 1})
    cache[key] = fetch(url)
    time.sleep(PACE)
  return cache[key][0] if cache[key] else None


def precisionOf(hit):
  if hit.get('category') in ['building', 'amenity', 'tourism', 'shop', 'aeroway', 'historic'] or hit.get('type') in ['hotel', 'mall', 'cathedral', 'church']:
    return 'building'
  if hit.get('category') == 'highway':
    return 'street'
  if hit.get('category') == 'place' and hit.get('type') in ['city', 'town', 'village', 'suburb']:
    return 'town'
  return 'area'


def elevations(points, cache):
  todo = [] if OFFLINE else [p for p in points if f"elevation:{p[0]:.5f},{p[1]:.5f}" not in cache]
  for i in range(0, len(todo), 100):
    batch = todo[i:i + 100]
    url = 'https://api.opentopodata.org/v1/srtm30m?locations=' + '|'.join(f"{a:.5f},{b:.5f}" for a, b in batch)
    for r in fetch(url).get('results', []):
      loc = r['location']
      cache[f"elevation:{loc['lat']:.5f},{loc['lng']:.5f}"] = r.get('elevation')
    time.sleep(PACE)
  return {p: cache.get(f"elevation:{p[0]:.5f},{p[1]:.5f}") for p in points}


def osmFromWikidata(ids, cache):
  todo = [] if OFFLINE else [i for i in ids if f"wikidata:{i}" not in cache]
  for k in range(0, len(todo), 200):
    batch = todo[k:k + 200]
    query = 'SELECT ?gn ?osm WHERE { VALUES ?gn { ' + ' '.join(f'"{i}"' for i in batch) + ' } ?item wdt:P1566 ?gn . ?item wdt:P402 ?osm . }'
    request = urllib.request.Request('https://query.wikidata.org/sparql', data=urllib.parse.urlencode({'query': query, 'format': 'json'}).encode(), headers={'User-Agent': USER_AGENT, 'Accept': 'application/sparql-results+json'})
    with urllib.request.urlopen(request, timeout=120) as r:
      rows = json.loads(r.read().decode('utf-8'))['results']['bindings']
    for i in batch:
      cache[f"wikidata:{i}"] = None
    for row in rows:
      cache[f"wikidata:{row['gn']['value']}"] = 'relation/' + row['osm']['value']
    time.sleep(PACE)
  return {i: cache.get(f"wikidata:{i}") for i in ids}


def geonamesRecords(ids):
  found = {}
  if not ids:
    return found
  with open(GEONAMES_DIR + 'allCountries.txt', encoding='utf-8') as fp:
    for line in fp:
      gid = int(line[:line.index('\t')])
      if gid in ids:
        f = line.rstrip('\n').split('\t')
        found[gid] = {'name': f[1], 'latitude': float(f[4]), 'longitude': float(f[5]), 'class': f[6], 'code': f[7], 'country': f[8], 'elevation': int(f[15]) if f[15] else None, 'dem': int(f[16]) if f[16] else None}
  return found


def distance(lat1, lon1, lat2, lon2):
  p1, p2 = math.radians(lat1), math.radians(lat2)
  a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
  return 6371 * 2 * math.asin(math.sqrt(a))


def country(code):
  return 'UK' if code == 'GB' else code


def precisionFromGeoNames(place):
  if place['class'] == 'A':
    return 'country' if place['code'].startswith('PCL') or place['code'] == 'TERR' else 'region'
  if place['class'] == 'L' and place['code'] in ['RGN', 'CONT']:
    return 'region'
  return {'P': 'town', 'S': 'building', 'R': 'street'}.get(place['class'], 'area')


def altitudeFromGeoNames(place):
  if place['class'] == 'A':
    return None
  if place['elevation'] is not None:
    return place['elevation']
  if place['dem'] is not None and place['dem'] > -9999:
    return place['dem']
  return None


def generated(geocoded, timeline, taken):
  entries = []
  for name in timeline['used']:
    hit = geocoded.get(name)
    if not hit or name.lower() in taken:
      continue
    taken.add(name.lower())
    place = hit['place']
    said = timeline['phrases'].get(name, [])
    entries.append({
      'location': name, 'type': 'venue' if place['class'] == 'S' else 'place', 'origin': 'generated',
      'placename': f"{place['name']}, {country(place['country'])}",
      'latitude': place['latitude'], 'longitude': place['longitude'], 'altitude': altitudeFromGeoNames(place),
      'precision': precisionFromGeoNames(place), 'geonames': place['geonames'],
      'notes': '; '.join(said[:3]) + (f" (and {len(said) - 3} more)" if len(said) > 3 else '') + f". GeoNames {place['class']}.{place['code']}" + (f", {hit['alternatives']} other places of this name" if hit['alternatives'] else ''),
    })
  for name, dates in sorted(timeline['unresolved'].items()):
    if name.lower() in taken:
      continue
    taken.add(name.lower())
    entries.append({
      'location': name, 'type': 'unresolved', 'origin': 'generated', 'latitude': None, 'longitude': None,
      'notes': f"\"coming to you from {name}\" in the transcript of {', '.join(dates[:5])}" + (f" (and {len(dates) - 5} more)" if len(dates) > 5 else ''),
    })
  return entries


def dump(entry):
  lines = []
  for field in FIELDS:
    if field not in entry:
      continue
    value = entry[field]
    if field == 'recorded':
      if value:
        lines.append('  recorded:')
        for p in value:
          lines.append(f"  - from: {p['from']}\n    to: {p['to']}")
      continue
    if field == 'at':
      if value:
        lines.append('  at:')
        for p in value:
          lines.append(f"  - from: {p['from']}\n    to: {p['to']}\n    shows: {p['shows']}\n    stated: {p['stated']}\n    confirmed: {p.get('confirmed', 0)}")
      continue
    if field == 'notes' and value and len(value) > 100:
      words, line, out = value.split(' '), '   ', []
      for w in words:
        if len(line) + len(w) > 116:
          out.append(line)
          line = '   '
        line += ' ' + w
      out.append(line)
      lines.append('  notes: >-\n' + '\n'.join(out))
      continue
    text = yaml.safe_dump({field: value}, allow_unicode=True, default_flow_style=isinstance(value, list), width=1000, sort_keys=False).rstrip('\n')
    text = text[1:-1] if text.startswith('{') else text
    lines.append('- ' + text if field == 'location' else '  ' + text)
  return '\n'.join(lines) + '\n'


def main():
  global OFFLINE
  OFFLINE = '--offline' in sys.argv
  args = [a for a in sys.argv[1:] if not a.startswith('--')]
  with open(LOCATIONS) as fp:
    entries = yaml.safe_load(fp)['locations']
  curated = [e for e in entries if e.get('origin') != 'generated']
  for e in curated:
    e['origin'] = 'curated'

  taken = set()
  for e in curated:
    taken.update(n.lower() for n in [e['location']] + list(e.get('aliases') or []))
  extra = []
  timeline = None
  if len(args) > 1:
    with open(args[0]) as fp:
      geocoded = json.load(fp)
    with open(args[1]) as fp:
      timeline = json.load(fp)
    extra = generated(geocoded, timeline, taken)
  entries = curated + extra

  cache = loadCache()
  records = geonamesRecords({e['geonames'] for e in curated if e.get('geonames') and e.get('latitude') is None})
  for e in curated:
    place = records.get(e.get('geonames'))
    if place and e.get('latitude') is None:
      e['latitude'], e['longitude'] = place['latitude'], place['longitude']
      e['precision'] = e.get('precision') or precisionFromGeoNames(place)
      if e.get('altitude') is None:
        e['altitude'] = altitudeFromGeoNames(place)
  for e in curated:
    if e.get('latitude') is None and e.get('query'):
      hit = nominatim(e['query'], cache)
      saveCache(cache)
      if hit:
        e['latitude'], e['longitude'] = round(float(hit['lat']), 6), round(float(hit['lon']), 6)
        e['osm'] = f"{hit['osm_type']}/{hit['osm_id']}"
        e['precision'] = e.get('precision') or precisionOf(hit)
      else:
        print(f"not found: {e['query']}")
  osm = osmFromWikidata(sorted({str(e['geonames']) for e in entries if e.get('geonames') and not e.get('osm')}), cache)
  saveCache(cache)
  for e in entries:
    if e.get('geonames') and not e.get('osm'):
      e['osm'] = osm.get(str(e['geonames']))
  for e in entries:
    if e.get('geonames') and not e.get('osm') and e.get('latitude') is not None and e.get('placename'):
      hit = nominatim(f"{e['location']}, {e['placename'].split(', ')[-1].replace('UK', 'United Kingdom')}", cache)
      saveCache(cache)
      if hit and distance(e['latitude'], e['longitude'], float(hit['lat']), float(hit['lon'])) < 25:
        e['osm'] = f"{hit['osm_type']}/{hit['osm_id']}"
  points = sorted({(e['latitude'], e['longitude']) for e in entries if e.get('latitude') is not None and e.get('altitude') is None and e.get('precision') not in ['country', 'region']})
  heights = elevations(points, cache)
  saveCache(cache)
  for e in entries:
    if e.get('latitude') is not None and e.get('altitude') is None and e.get('precision') not in ['country', 'region']:
      h = heights.get((e['latitude'], e['longitude']))
      e['altitude'] = round(h) if h is not None else None

  if timeline:
    for e in entries:
      e['at'] = [{k: v for k, v in p.items() if k != 'location'} for p in timeline['periods'] if p['location'] == e['location']] or None

  out = [HEADER, '\nlocations:\n']
  for kind, title in SECTIONS:
    group = [e for e in entries if e.get('type') == kind]
    if not group:
      continue
    out.append(f"\n# {title}\n")
    for e in group:
      out.append('\n' + dump(e))
  others = [e for e in entries if e.get('type') not in [k for k, _ in SECTIONS]]
  for e in others:
    out.append('\n' + dump(e))
  with open(LOCATIONS, 'w') as fp:
    fp.write(''.join(out))
  resolved = sum(1 for e in entries if e.get('latitude') is not None)
  print(f"{len(entries)} locations ({len(curated)} curated), {resolved} with coordinates, {len(entries) - resolved} to resolve")


if __name__ == '__main__':
  main()
