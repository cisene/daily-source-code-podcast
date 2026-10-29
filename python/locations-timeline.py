#!/usr/bin/env python3
import os
import re
import sys
import glob
import html
import json
import math
import yaml
import datetime
import email.utils
import importlib.util

spec = importlib.util.spec_from_file_location('geocode', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locations-geocode.py'))
geocode = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geocode)

LOCATIONS = '../yaml/locations.yaml'
INTRO = 6000
PRIORITY = {'venue': 0, 'vehicle': 0, 'residence': 1, 'place': 2}
FINENESS = {'building': 0, 'street': 0, 'area': 1, 'town': 1, 'region': 2, 'country': 3}
STOP = {'delta', 'sierra', 'charlie', 'delta sierra', 'source code', 'adam', 'curry', 'podshow', 'mevio', 'itunes', 'friday', 'monday', 'tuesday', 'wednesday', 'thursday', 'saturday', 'sunday', 'home', 'here', 'there', 'studio', 'the road', 'road', 'europe', 'america', 'cottage', 'condo', 'manor', 'castle', 'bunker', 'terrace', 'avenue', 'west side', 'watch tower', 'nice', 'cisco', 'serino', 'york', 'kate', 'western', 'derby'}

SPELLINGS = [
  (r"\b(Curie|Curri|Kari|Kori|Couri|Kroy|Currie|Curey|Corey)\s*(?=Cottage|Condo|Manor|Castle|Coast|Terrace)", 'Curry '),
  (r"\bCurry\s*(Kondo|Condu|Condol|condo)\b|\bCurricondo\b|\bRecondo\b", 'Curry Condo'),
  (r"\bCouricotteage\b|\bCurricanage\b|\bCurry\s*Cotage\b", 'Curry Cottage'),
  (r"\bCurry Council\b", 'Curry Castle'),
  (r"\bGuil?ford\b|\bGilford\b|\bGuilford\b", 'Guildford'),
  (r"\bSkippal\b|\bSchipol\b|\bSkiphol\b", 'Schiphol'),
  (r"\bHill ?top,? Watch ?tower\b|\bHiltop,? Watch ?Tower\b", 'Hilltop Watchtower'),
  (r"\bCurry manner\b|\bcareer manager\b", 'Curry Manor'),
  (r"\bthe (cottage|condo|manor|castle|bunker|terrace)\b", lambda m: 'the Curry ' + m.group(1).capitalize()),
  (r"\b(?:Serino|Surin|Suri|Surrey|Sorry)\s+(?:known )?as\b", 'Surrey known as'),
  (r"\bgulford\b|\bGuildfor\b", 'Guildford'),
  (r"\bFranscisco\b", 'Francisco'),
  (r"\bNew York(?! City)\b", 'New York City'),
  (r"\bthe States\b", 'the United States'),
  (r"(?-i:\bSF\b)", 'San Francisco'),
  (r"\bStar(?:box|bucks)\b(?=[^.]{0,40}\bGuildford\b)", 'Starbucks Market Street Guildford'),
]
CONTINENTS = {'europe': 'EU', 'north america': 'NA', 'america': 'NA', 'asia': 'AS', 'africa': 'AF', 'south america': 'SA', 'oceania': 'OC', 'australia': 'OC'}
COUNTRY_INTRO = 3000
FROM = re.compile(r"(?:coming to you|live|broadcasting|recording|podcasting|reporting|welcome|greetings)(?: \w+){0,3}? from (?:the |a |my |our |beautiful |lovely |sunny |downtown )*(.{0,90})", re.I)
AT = re.compile(r"\b(?:I'm|I am|we're|we are|here|sitting|hanging out)(?: back| right| live| currently| now| still| actually)? (?:in|at) (?:the |a |my |beautiful |lovely |sunny |downtown )*(.{0,70})", re.I)
NOTES_LIVE = re.compile(r"(?<!our )\b[Ll]ive [Ff]rom (?:the |The )?([A-Z][^\n.!]{2,80})")
BACK_REFERENCE = re.compile(r"(?i)\b(?:last time|we spoke|when I was|when we were|yesterday|the other day|used to)\b")
NOTES = re.compile(r"(?:^|\n|\. )\s*(?:- \[[ xX]\] )?(?:Live |Recorded |Almost live )?[Ff]rom (?:the |The )?([A-Z][^\n]{2,120})")
TS = re.compile(r'^\d+$|-->')
IGNORE = re.compile(r"broadcast from Camp Smitty|Newark, Ohio|infield at the Kentucky Derby", re.I)
BLOG = '../json/blog-posts.json'
BLOG_SAID = re.compile(r"(?:\b(?:I'm|I am|we're|we are|here|currently|still|now)(?: back| now| currently| still| here)? (?:in|at)|\b(?:arrived|landed|touched down|checked in|staying|holed up)(?: here)? (?:in|at)|\bgreetings from|\blive from|\bcoming to you from|\bback home in|\bwriting (?:this )?from) (?:the |a |my |beautiful |lovely |sunny |rainy |downtown )*(.{0,80})", re.I)
BLOG_BACK = re.compile(r"\b(?i:(?:I'm|I am|we're|we are|I'll be|we'll be)(?: \w+)? back|first (?:day|night) back|(?:just|finally|safely) back) (?i:in|home in) ([A-Z][\w'’.-]*(?: [A-Z][\w'’.-]*)*)")
FLIGHT = re.compile(r"\b(?:we are|we're|I'm|I am) (?:on|aboard) (?:[A-Z][\w-]* ){1,3}flight (?:number )?\d+", re.I)
TOWN_IN = re.compile(r"([A-Z][\w'’.-]*(?: [A-Z][\w'’.-]*)*), ([A-Z][\w'’.-]*(?: [A-Z][\w'’.-]*)*)")
TOWN_OF = re.compile(r"(?:\w+ )?(?:town|city|village|hamlet) of ([A-Z][\w'’.-]*(?: [A-Z][\w'’.-]*)*)")
CAPITALS = re.compile(r"^((?:[A-Z][\w'’.-]*)(?: (?:[A-Z][\w'’.-]*|of|on|in|de|van))*)")


def normalise(text):
  for pattern, replacement in SPELLINGS:
    text = re.sub(pattern, replacement, text, flags=re.I if isinstance(replacement, str) else re.I)
  return text


def loadNames(locations):
  names = []
  for entry in locations:
    for name in [entry['location']] + list(entry.get('aliases') or []):
      if name and name.lower() not in STOP and len(name) > 2:
        names.append((name.lower(), entry))
  names.sort(key=lambda n: -len(n[0]))
  return [(re.compile(r'\b' + re.escape(n) + r'\b', re.I), entry) for n, entry in names]


def findIn(phrase, names, fits=lambda entry: True):
  hits = []
  taken = []
  for pattern, entry in names:
    if not fits(entry):
      continue
    for m in pattern.finditer(phrase):
      if any(m.start() < b and a < m.end() for a, b in taken):
        continue
      taken.append((m.start(), m.end()))
      hits.append((entry.get('origin') == 'generated', PRIORITY.get(entry.get('type'), 3), FINENESS.get(entry.get('precision'), 1), m.start(), entry))
  return min(hits, key=lambda h: h[:4])[4] if hits else None


SHOW_DATE_FIXES = {
  '2006/DSC-2006-10-31.mp3': '2006-11-02',
  '2008/DSC-2008-04-25.mp3': '2008-04-23',
  '2008/DSC-2008-05-07-1.mp3': '2008-05-09',
}
MONTH_NAMES = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']


def titleDate(title):
  m = re.search(r"(?i)\b(" + '|'.join(MONTH_NAMES) + r")\s+(\d{1,2})(?:st|nd|rd|th|d)?,?\s+(20[01]\d)", str(title or ''))
  return f"{m.group(3)}-{MONTH_NAMES.index(m.group(1).lower()) + 1:02}-{int(m.group(2)):02}" if m else None


def pubDateDate(pubDate):
  try:
    return email.utils.parsedate_to_datetime(str(pubDate)).strftime("%Y-%m-%d")
  except (TypeError, ValueError):
    pass
  m = re.search(r"^\w{3} (\w{3}) +(\d{1,2}) [\d:]+ (\d{4})", str(pubDate or ''))
  months = [n[:3] for n in MONTH_NAMES]
  return f"{m.group(3)}-{months.index(m.group(1).lower()) + 1:02}-{int(m.group(2)):02}" if m and m.group(1).lower() in months else None


def showDate(ep):
  source = str((ep.get('fileinfo') or {}).get('source') or '') if isinstance(ep.get('fileinfo'), dict) else ''
  if source in SHOW_DATE_FIXES:
    return SHOW_DATE_FIXES[source]
  m = re.search(r'(\d{4}-\d\d-\d\d)', source) or re.search(r'(\d{4}-\d\d-\d\d)', str(ep.get('pubDate')))
  return m.group(1) if m else titleDate(ep.get('title')) or pubDateDate(ep.get('pubDate'))


def showDates():
  dates = {}
  for path in sorted(glob.glob('../yaml/episodes/[0-9]*.yaml')):
    try:
      with open(path) as fp:
        ep = yaml.safe_load(fp)
    except Exception:
      continue
    if not isinstance(ep, dict):
      continue
    date = showDate(ep)
    if not date:
      continue
    description = ep.get('description') if isinstance(ep.get('description'), str) else ''
    dates.setdefault(date, {'notes': [], 'srt': None})['notes'].append(html.unescape(re.sub(r'<[^>]+>', '\n', description.replace('\\n', '\n'))))
  for path in sorted(glob.glob('../srt/*/DSC-*.srt')):
    m = re.search(r'DSC-(\d{4}-\d\d-\d\d)(-\d)?\.srt$', path)
    if m:
      audio = f"{m.group(1)[:4]}/DSC-{m.group(1)}{m.group(2) or ''}.mp3"
      if m.group(2) and audio not in SHOW_DATE_FIXES:
        continue
      date = SHOW_DATE_FIXES.get(audio, m.group(1))
      dates.setdefault(date, {'notes': [], 'srt': None})['srt'] = path
  return dates


def curated(entry):
  return entry.get('origin') != 'generated'


def townOrSmaller(entry):
  return curated(entry) or entry.get('precision') in ['town', 'building', 'street', 'area']


def stated(show, names, unresolved, date):
  for text in show['notes']:
    for m in NOTES.finditer(text[:600]):
      entry = findIn(normalise(m.group(1)), names)
      if entry:
        for live in NOTES_LIVE.finditer(text):
          other = findIn(normalise(live.group(1)), names)
          if other and other['location'] != entry['location'] and live.start() > m.start():
            return other, 'notes', live.group(0).strip()
        return entry, 'notes', m.group(0).strip()
  if not show['srt']:
    return None, None, None
  with open(show['srt'], encoding='utf-8', errors='replace') as fp:
    text = ' '.join(l.strip() for l in fp if l.strip() and not TS.search(l.strip()))
  text = normalise(text[:INTRO])
  found = []
  loose = []
  for m in FROM.finditer(text):
    if IGNORE.search(m.group(0)):
      continue
    entry = findIn(BACK_REFERENCE.split(m.group(1))[0], names, townOrSmaller)
    if entry:
      found.append((m.start(), entry, m.group(0)))
    elif CAPITALS.match(m.group(1)) and not findIn(m.group(1), names):
      loose.append(CAPITALS.match(m.group(1)).group(1).strip(" .'"))
  flight = FLIGHT.search(text)
  inflight = [e for _, e in names if e['location'] == 'In flight']
  if flight and inflight:
    found.append((flight.start(), inflight[0], flight.group(0)))
  for m in AT.finditer(text):
    entry = None if IGNORE.search(m.group(0)) else findIn(m.group(1), names, curated)
    if not entry and not IGNORE.search(m.group(0)) and TOWN_OF.match(m.group(1)):
      entry = findIn(TOWN_OF.match(m.group(1)).group(1), names, townOrSmaller)
    if not entry and not IGNORE.search(m.group(0)) and TOWN_IN.match(m.group(1)):
      town, wider = TOWN_IN.match(m.group(1)).groups()
      town = findIn(town, names, townOrSmaller)
      wider = findIn(wider, names, lambda e: e.get('precision') in ['region', 'country'])
      if town and wider and countryOf(town) == wider.get('country'):
        entry = town
    if entry:
      found.append((m.start(), entry, m.group(0)))
  if found:
    start, entry, phrase = min(found, key=lambda f: f[0])
    return entry, 'transcript', phrase
  wide = []
  for said in [FROM, AT]:
    for m in said.finditer(text[:COUNTRY_INTRO]):
      entry = None if IGNORE.search(m.group(0)) else findIn(m.group(1), names, lambda e: e.get('precision') in ['country', 'region'])
      if entry and entry.get('country'):
        wide.append((m.start(), entry, m.group(0)))
  if wide:
    start, entry, phrase = min(wide, key=lambda f: f[0])
    return entry, 'country', phrase
  for name in loose:
    name = re.sub(r"\s+(With|And|It|It's|This|That|The)$", '', name)
    if name.lower() not in STOP and len(name) > 2 and name not in ['And', 'The', 'This', 'That', 'It']:
      unresolved.setdefault(name, []).append(date)
  return None, None, None


REGION_KM = 400
NEAR_KM = 25


def distance(lat1, lon1, lat2, lon2):
  p1, p2 = math.radians(lat1), math.radians(lat2)
  a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
  return 6371 * 2 * math.asin(math.sqrt(a))


def countryInfo():
  continents = {}
  with open(geocode.GEONAMES_DIR + 'countryInfo.txt', encoding='utf-8') as fp:
    for line in fp:
      if not line.startswith('#'):
        f = line.split('\t')
        continents[f[0]] = f[8]
  return continents


continentOf = countryInfo()


def countryOf(entry):
  if entry.get('country'):
    return entry['country']
  m = re.search(r', ([A-Z]{2})$', entry.get('placename') or '')
  return None if not m else ('GB' if m.group(1) == 'UK' else m.group(1))


def agrees(current, statement):
  if statement.get('precision') == 'region' and not statement.get('wide') and None not in (current.get('latitude'), statement.get('latitude')):
    return distance(current['latitude'], current['longitude'], statement['latitude'], statement['longitude']) < REGION_KM
  country = countryOf(current)
  if country is None:
    return True
  if statement.get('wide'):
    return continentOf.get(country) == statement.get('continent')
  return country == statement.get('country')


def blogStatements(names):
  try:
    with open(BLOG) as fp:
      posts = json.load(fp)
  except (OSError, ValueError):
    return {}
  found = {}
  for post in posts:
    body = normalise(f"{post.get('title') or ''}. {post.get('text') or ''}".replace('’', "'"))
    hits = []
    for m in list(BLOG_SAID.finditer(body)) + list(BLOG_BACK.finditer(body)):
      if IGNORE.search(m.group(0)):
        continue
      entry = findIn(re.split(r'[.!?\n]', m.group(1))[0], names)
      if entry and not entry.get('wide'):
        hits.append((entry, m.group(0), post.get('permalink')))
    hits.sort(key=lambda hit: not townOrSmaller(hit[0]))
    if hits:
      found.setdefault(post['date'], []).append(hits[0])
  return found


def fromBlog(blog, date, days=1):
  day = datetime.date.fromisoformat(date)
  for d in [day - datetime.timedelta(days=n) for n in range(days + 1)]:
    said = blog.get(d.isoformat())
    if said:
      return ([s for s in said if townOrSmaller(s[0])] or said)[-1]
  return None


def gazetteer(path):
  with open(path) as fp:
    geocoded = json.load(fp)
  entries = []
  for name, hit in geocoded.items():
    place = hit['place']
    if place['class'] == 'A':
      precision = 'country' if place['code'].startswith('PCL') else 'region'
    elif place['class'] == 'L' and place['code'] in ['CONT', 'RGN']:
      precision = 'region'
    else:
      precision = {'P': 'town', 'S': 'building'}.get(place['class'], 'area')
    aliases = [w for w, right in geocode.SPELLINGS.items() if right == name and len(w) > 3]
    continent = CONTINENTS.get(name.lower()) if place['code'] == 'CONT' else continentOf.get(place['country'])
    entries.append({'location': name, 'aliases': aliases, 'type': 'venue' if place['class'] == 'S' else 'place', 'origin': 'generated', 'precision': precision,
                    'country': place['country'] or None, 'continent': continent, 'wide': place['code'] == 'CONT',
                    'latitude': place['latitude'], 'longitude': place['longitude']})
  return entries


def main():
  if len(sys.argv) < 3:
    print('Usage: locations-timeline.py GEOCODED.json TIMELINE.json [REPORT.tsv]')
    sys.exit(2)
  with open(LOCATIONS) as fp:
    locations = [e for e in yaml.safe_load(fp)['locations'] if e.get('origin') != 'generated']
  names = loadNames(locations + gazetteer(sys.argv[1]))
  blog = blogStatements(names)

  rows = []
  unresolved = {}
  current = None
  hand = [(str(p['from']), str(p['to']), e) for e in locations for p in (e.get('recorded') or [])]
  for date, show in sorted(showDates().items()):
    byhand = [e for a, b, e in hand if a <= date <= b]
    if byhand:
      current = byhand[0]
      rows.append((date, current, 'hand', 'recorded (set by hand in locations.yaml)'))
      continue
    entry, how, phrase = stated(show, names, unresolved, date)
    if how in [None, 'country']:
      said = fromBlog(blog, date, 2 if how is None else 1)
      if said and townOrSmaller(said[0]) and not (how == 'country' and not agrees(said[0], entry)):
        entry, how, phrase = said[0], 'blog', f"{said[1]} ({said[2]})"
      elif said and how is None:
        entry, how, phrase = said[0], 'country', f"blog: {said[1]} ({said[2]})"
    if how in ['transcript', 'blog'] and current and not curated(entry) and townOrSmaller(entry) and curated(current) \
       and None not in (current.get('latitude'), entry.get('latitude')) \
       and distance(current['latitude'], current['longitude'], entry['latitude'], entry['longitude']) < NEAR_KM:
      entry, how = current, 'confirmed'
    if how == 'country':
      if current and agrees(current, entry):
        how = 'confirmed'
      else:
        current = entry
    elif entry:
      current = entry
    elif current:
      how = 'carried'
    rows.append((date, current, how, phrase))

  spans = []
  for date, entry, how, phrase in rows:
    if entry is None:
      continue
    if spans and spans[-1]['location'] == entry['location']:
      spans[-1]['to'] = date
      spans[-1]['shows'] += 1
    else:
      spans.append({'location': entry['location'], 'from': date, 'to': date, 'shows': 1, 'stated': 0, 'confirmed': 0})
    spans[-1]['stated'] += how in ['notes', 'transcript', 'country', 'hand', 'blog']
    spans[-1]['confirmed'] += how == 'confirmed'
  phrases = {}
  for date, entry, how, phrase in rows:
    if entry and how in ['notes', 'transcript', 'country', 'blog']:
      phrases.setdefault(entry['location'], []).append(f"{re.sub(r'\s+', ' ', phrase)[:120]} ({date})")
  used = sorted({e['location'] for _, e, how, _ in rows if e and how in ['notes', 'transcript', 'country', 'blog'] and e.get('origin') == 'generated'})
  with open(sys.argv[2], 'w') as fp:
    json.dump({'periods': spans, 'used': used, 'phrases': phrases, 'unresolved': unresolved}, fp, indent=1, ensure_ascii=False)

  if len(sys.argv) > 3:
    with open(sys.argv[3], 'w') as fp:
      for date, entry, how, phrase in rows:
        fp.write(f"{date}\t{entry['location'] if entry else ''}\t{how or ''}\t{re.sub(r'\s+', ' ', phrase or '')[:160]}\n")
  counts = {}
  for _, _, how, _ in rows:
    counts[how] = counts.get(how, 0) + 1
  print(f"{len(rows)} show dates: {counts}, {len(spans)} periods, {len(used)} places from the shows, {len(unresolved)} unresolved names")


if __name__ == '__main__':
  main()
