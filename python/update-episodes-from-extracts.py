#!/usr/bin/env python3
import os
import re
import sys
import glob
import json
import types
import datetime
import importlib.util

EPISODE_DIR = '../yaml/episodes/'
EXTRACT_DIR = '../rss/episodes/'
TAGS_FILE = '../json/dsc-archive-tag-enclosures.json'
EPISODE_LAST = 867

TITLE_FIXES = {
  'dailysourcecode-280880-05-15-2011.mp3': ('April 16 3011', 'April 16 2011'),
}


def loadScript(name, filename, stubs=[]):
  for stub in stubs:
    sys.modules.setdefault(stub, types.ModuleType(stub))
  spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


audio = loadScript('audio', 'update-episodes-from-audio.py')
posts = loadScript('posts', 'update-episodes-from-posts.py', stubs=['feedparser'])


def enclosureName(extract):
  return os.path.basename(str(audio.get(extract, 'enclosure', 'url')))


def itemTitleDate(extract):
  title = str(extract.get('title'))
  if enclosureName(extract) in TITLE_FIXES:
    title = title.replace(*TITLE_FIXES[enclosureName(extract)])
  return posts.dateFromTitle(title)


def itemNumber(extract):
  m = re.search(r"^#\s?(\d{3})\b", str(audio.get(extract, 'itunes', 'subtitle') or '').strip())
  return int(m.group(1)) if m else None


def agrees(n, ep, extract, file_title=None):
  m = re.search(r"^#\s?(\d{3})\b", str(file_title or '').strip())
  if m:
    return int(m.group(1)) == n and itemNumber(extract) in [None, n]
  if itemNumber(extract) != None:
    return itemNumber(extract) == n
  title_date = itemTitleDate(extract)
  return title_date != None and title_date in [posts.dateFromTitle(ep.get('title')), posts.episodeShowDate(ep)]


def replaceable(value, placeholder, wrong):
  return posts.isPlaceholder(value, placeholder) or (wrong != None and value == wrong)


def updateEpisode(n, ep, extract, log, wrong=None):
  changes = []
  wrong = wrong or {}

  link = extract.get('link')
  if posts.hasScheme(link) and link != ep.get('originalLink') and replaceable(ep.get('originalLink'), '#daily-source-code-episode-web', wrong.get('link')):
    ep['originalLink'] = link
    changes.append('originalLink')

  guid = audio.get(extract, 'guid', 'link')
  if posts.hasScheme(guid) and isinstance(ep.get('guid'), dict) and guid != ep['guid'].get('link') and replaceable(ep['guid'].get('link'), '#daily-source-code-episode-guid', audio.get(wrong, 'guid', 'link')):
    ep['guid']['link'] = guid
    if audio.get(extract, 'guid', 'isPermaLink') != None:
      ep['guid']['isPermaLink'] = audio.get(extract, 'guid', 'isPermaLink')
    changes.append('guid')

  pubDate = extract.get('pubDate')
  if pubDate != None and not posts.isDateOnly(pubDate) and pubDate != ep.get('pubDate') and (posts.isDateOnly(ep.get('pubDate')) or ep.get('pubDate') == wrong.get('pubDate')):
    old_pubDate = ep.get('pubDate')
    ep['pubDate'] = pubDate
    for ns in ['itunes', 'podcast']:
      if isinstance(ep.get(ns), dict) and 'pubDate' in ep[ns] and (posts.isDateOnly(ep[ns]['pubDate']) or ep[ns]['pubDate'] == old_pubDate):
        ep[ns]['pubDate'] = pubDate
    changes.append('pubDate')

  url = audio.get(extract, 'enclosure', 'url')
  old_url = audio.get(ep, 'enclosure', 'url')
  if posts.hasScheme(url) and url != old_url and (not posts.hasScheme(old_url) or old_url == audio.get(wrong, 'enclosure', 'url')):
    ep['enclosure']['url'] = url
    for ae in audio.alternateEnclosures(ep):
      if isinstance(ae.get('source'), dict) and os.path.basename(str(old_url)) in audio.sourceBasenames(ae) and (not posts.hasScheme(ae['source'].get('uri')) or ae['source'].get('uri') == old_url):
        ae['source']['uri'] = url
    changes.append('enclosure url')

  text = extract.get('description')
  if text != None and str(text).strip() != '' and audio.isPlaceholderDescription(ep.get('description')):
    duration = audio.get(ep, 'fileinfo', 'duration')
    old_description = ep.get('description')
    ep['description'] = audio.withDuration(text, duration) if duration != None else text
    for ns in ['itunes', 'podcast']:
      summary = audio.get(extract, ns, 'summary') or audio.get(extract, 'itunes', 'summary')
      if summary != None and isinstance(ep.get(ns), dict) and 'summary' in ep[ns]:
        if ep[ns]['summary'] == old_description or audio.isPlaceholderDescription(ep[ns]['summary']):
          ep[ns]['summary'] = summary
    changes.append('description')

  if len(changes) > 0:
    log.append(f"{n:03}: {', '.join(changes)}{' (replacing ' + enclosureName(wrong) + ')' if wrong else ''}")
  return len(changes) > 0


def main():
  dry_run = '--dry-run' in sys.argv

  byname = {}
  extracts = {}
  for path in sorted(glob.glob(f"{EXTRACT_DIR}*.yaml")):
    extract = audio.readYAML(path)
    if not isinstance(extract, dict) or audio.get(extract, 'enclosure', 'url') == None:
      continue
    if enclosureName(extract) in byname:
      continue
    byname[enclosureName(extract)] = extract
    ymd = posts.dateFromName(audio.get(extract, 'enclosure', 'url'))
    if ymd != None:
      extracts.setdefault(ymd, []).append(extract)

  with open(TAGS_FILE) as fp:
    tagged = json.load(fp)

  episodes = {}
  holders = {}
  for n in range(1, EPISODE_LAST + 1):
    ep = audio.readYAML(f"{EPISODE_DIR}{n:03}.yaml")
    if not isinstance(ep, dict) or not isinstance(ep.get('fileinfo'), dict) or not isinstance(ep.get('podcast'), dict):
      continue
    episodes[n] = ep
    ymd = posts.episodeShowDate(ep)
    if ymd != None:
      holders.setdefault(ymd, []).append(n)

  log = []
  skipped = []
  changed = set()
  claimed = set()
  matched = set()

  for n, ep in episodes.items():
    tags = tagged.get(audio.get(ep, 'fileinfo', 'source')) or {}
    names = [os.path.basename(u) for u in tags.get('urls', [])]
    items = [byname[name] for name in dict.fromkeys(names) if name in byname]
    if len(items) != 1:
      continue
    extract = items[0]
    if not agrees(n, ep, extract, tags.get('title')):
      skipped.append(f"{n:03}: tags of {audio.get(ep, 'fileinfo', 'source')} name {enclosureName(extract)} titled {extract.get('title')!r}, not this episode")
      continue
    claimed.add(enclosureName(extract))
    matched.add(n)
    wrong = byname.get(os.path.basename(str(audio.get(ep, 'enclosure', 'url'))))
    if wrong is extract:
      wrong = None
    if updateEpisode(n, ep, extract, log, wrong):
      log[-1] += f" by archive tags"
      changed.add(n)

  for extract in byname.values():
    n = itemNumber(extract)
    if n == None or n not in episodes or n in matched or enclosureName(extract) in claimed:
      continue
    show = posts.episodeShowDate(episodes[n])
    published = posts.dateFromName(audio.get(extract, 'enclosure', 'url'))
    if show == None or published == None or abs((datetime.date.fromisoformat(show) - datetime.date.fromisoformat(published)).days) > 3:
      skipped.append(f"{n:03}: {enclosureName(extract)} states #{n}, audio is {show}")
      continue
    claimed.add(enclosureName(extract))
    matched.add(n)
    log.append(f"{n:03}: matched by stated number, enclosure {enclosureName(extract)}")
    wrong = byname.get(os.path.basename(str(audio.get(episodes[n], 'enclosure', 'url'))))
    if updateEpisode(n, episodes[n], extract, log, None if wrong is extract else wrong):
      changed.add(n)

  for ymd, numbers in sorted(holders.items()):
    found = [e for e in extracts.get(ymd, []) if enclosureName(e) not in claimed]
    numbers = [n for n in numbers if n not in matched]
    if len(found) == 0 or len(numbers) == 0:
      continue
    if len(numbers) > 1:
      skipped.append(f"{ymd}: {', '.join(f'{n:03}' for n in numbers)} hold the same show")
      continue
    if len(found) > 1:
      skipped.append(f"{ymd}: {len(found)} feed items carry this date: {', '.join(enclosureName(e) for e in found)}")
      continue
    n = numbers[0]
    claimed.add(enclosureName(found[0]))
    matched.add(n)
    if updateEpisode(n, episodes[n], found[0], log):
      changed.add(n)

  unmatched = []
  for ymd, found in sorted(extracts.items()):
    for extract in found:
      if enclosureName(extract) in claimed:
        continue
      title_date = itemTitleDate(extract)
      numbers = [n for n in holders.get(title_date, []) if n not in matched]
      if title_date == None or len(numbers) != 1:
        unmatched.append(f"{ymd}: {enclosureName(extract)} titled {extract.get('title')!r}")
        continue
      n = numbers[0]
      claimed.add(enclosureName(extract))
      matched.add(n)
      log.append(f"{n:03}: matched by title date {title_date}, enclosure {enclosureName(extract)}")
      if updateEpisode(n, episodes[n], extract, log):
        changed.add(n)

  for n, ep in episodes.items():
    if n in matched or posts.hasScheme(audio.get(ep, 'enclosure', 'url')):
      continue
    names = [os.path.basename(u) for u in (tagged.get(audio.get(ep, 'fileinfo', 'source')) or {}).get('urls', [])]
    items = [byname[name] for name in dict.fromkeys(names) if name in byname and name not in claimed]
    if len(items) != 1:
      continue
    extract = items[0]
    claimed.add(enclosureName(extract))
    matched.add(n)
    unmatched = [u for u in unmatched if not u.startswith(f"{posts.dateFromName(enclosureName(extract))}: {enclosureName(extract)} ")]
    log.append(f"{n:03}: matched by archive tags only, {enclosureName(extract)} titled {extract.get('title')!r}, episode titled {ep.get('title')!r}")
    if updateEpisode(n, ep, extract, log):
      changed.add(n)

  current = set(os.path.basename(str(audio.get(ep, 'enclosure', 'url'))) for ep in episodes.values())
  unmatched = [u for u in unmatched if u.split(' ')[1] not in current]

  if not dry_run:
    for n in sorted(changed):
      audio.writeYAML(f"{EPISODE_DIR}{n:03}.yaml", episodes[n])

  print("\n".join(log))
  print("")
  print(f"Episodes {'to update' if dry_run else 'updated'}: {len(changed)}")
  print(f"Skipped ({len(skipped)}):")
  print("\n".join(f"  {s}" for s in skipped))
  print(f"Feed items no episode audio matches ({len(unmatched)}):")
  print("\n".join(f"  {s}" for s in unmatched))


if __name__ == '__main__':
  main()
