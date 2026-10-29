#!/usr/bin/env python3
import os
import re
import sys
import glob
import json
import types
import locale
import importlib.util

EPISODE_DIR = '../yaml/episodes/'
POSTS_FILES = '../json/dsc-posts-*.json'
EPISODE_LAST = 867

ENCLOSURE_FIXES = {
  'http://homepage.mac.com/dailysourcecode/DSC/DSC-2005-03-29.mp3': 'http://homepage.mac.com/dailysourcecode/DSC/DSC-2005-03-30.mp3',
}

SKIP_ENCLOSURES = [
  'dailySourceCode08222004.mp3',
]

MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
MONTH_ABBR = {m[:3]: i + 1 for i, m in enumerate(MONTHS)}


def loadScript(name, filename, stubs=[]):
  for stub in stubs:
    sys.modules.setdefault(stub, types.ModuleType(stub))
  spec = importlib.util.spec_from_file_location(name, os.path.join(os.path.dirname(os.path.abspath(__file__)), filename))
  module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(module)
  return module


audio = loadScript('audio', 'update-episodes-from-audio.py')
rss = loadScript('rss', 'update-episodes-from-rss.py', stubs=['feedparser'])


def validDate(y, m, d):
  try:
    y, m, d = int(y), int(m), int(d)
  except (TypeError, ValueError):
    return None
  if 2004 <= y <= 2013 and 1 <= m <= 12 and 1 <= d <= 31:
    return f"{y:04}-{m:02}-{d:02}"
  return None


def dateFromName(name):
  name = os.path.basename(str(name or ''))
  m = re.search(r"(?i)^(?:deltasierracharl|dailysourcecode)-\d+-(\d{2})-(\d{2})-(\d{4})", name)
  if m:
    return validDate(m.group(3), m.group(1), m.group(2))
  m = re.search(r"(\d{4})-(\d{2})-(\d{2})", name)
  if m:
    return validDate(*m.groups())
  m = re.search(r"(\d{2})-(\d{2})-(\d{4})", name)
  if m:
    return validDate(m.group(3), m.group(2), m.group(1))
  m = re.search(r"(\d{1,2})-([A-Za-z]{3})[a-z]*-(\d{4})", name)
  if m and m.group(2).lower() in MONTH_ABBR:
    return validDate(m.group(3), MONTH_ABBR[m.group(2).lower()], m.group(1))
  m = re.search(r"(2004|2005)(\d{2})(\d{2})(2004|2005)?\.", name)
  if m:
    return validDate(*m.groups()[:3])
  m = re.search(r"(\d{2})(\d{2})(2004|2005)", name)
  if m:
    return validDate(m.group(3), m.group(1), m.group(2)) or validDate(m.group(3), m.group(2), m.group(1))
  return None


def dateFromTitle(title):
  m = re.search(r"(?i)\b(" + '|'.join(MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th|d)?,?\s+(20(?:0[4-9]|1[0-3]))", str(title or ''))
  if m:
    return validDate(m.group(3), MONTHS.index(m.group(1).lower()) + 1, m.group(2))
  return None


def isPlaceholder(value, prefix):
  return value == None or str(value).startswith(prefix)


def isDateOnly(value):
  return value == None or re.match(r"^\d{4}-\d{2}-\d{2}$", str(value)) != None


def hasScheme(url):
  return re.match(r"^https?://", str(url or '')) != None


def formatPubDate(pubDate):
  info = rss.parsePubDate(pubDate)
  if info == None:
    return None
  return info['pubDateFormatted']


def postShows(posts):
  shows = {}
  for post in posts:
    enclosure = post.get('enclosure') or {}
    url = ENCLOSURE_FIXES.get(enclosure.get('url'), enclosure.get('url'))
    if url == None or os.path.basename(url) in SKIP_ENCLOSURES:
      continue
    if not re.match(r"(?i)^(\d{3}-)?(dsc|dailysourcecode|deltasierracharl).*\.(mp3|m4a|mp4)$", os.path.basename(url)) or 'PPP' in url:
      continue
    ymd = dateFromName(url) or dateFromTitle(post.get('title'))
    if ymd == None:
      continue
    if any(p['enclosure']['url'] == url for p in shows.get(ymd, [])):
      continue
    fixed = dict(enclosure, url=url)
    if url != enclosure.get('url'):
      fixed['length'] = None
    post = dict(post, enclosure=fixed)
    shows.setdefault(ymd, []).append(post)
  return shows


def episodeShowDate(ep):
  return dateFromName(audio.get(ep, 'fileinfo', 'source')) or dateFromName(audio.get(ep, 'enclosure', 'url'))


def updateEpisode(n, ep, post, log):
  changes = []
  permalink = post['permalink']

  if isPlaceholder(ep.get('link'), '#daily-source-code-episode-web'):
    ep['link'] = permalink
    changes.append('link')
  if isinstance(ep.get('guid'), dict) and isPlaceholder(ep['guid'].get('link'), '#daily-source-code-episode-guid'):
    ep['guid']['link'] = permalink
    changes.append('guid')

  pubDate = formatPubDate(post.get('pubDate'))
  if pubDate != None and isDateOnly(ep.get('pubDate')):
    ep['pubDate'] = pubDate
    for ns in ['itunes', 'podcast']:
      if isinstance(ep.get(ns), dict) and 'pubDate' in ep[ns] and isDateOnly(ep[ns]['pubDate']):
        ep[ns]['pubDate'] = pubDate
    changes.append('pubDate')

  enclosure = post.get('enclosure') or {}
  old_url = audio.get(ep, 'enclosure', 'url')
  if enclosure.get('url') != None and not hasScheme(old_url):
    ep['enclosure']['url'] = enclosure['url']
    if isinstance(enclosure.get('length'), int):
      ep['enclosure']['length'] = enclosure['length']
    for ae in audio.alternateEnclosures(ep):
      if not isinstance(ae.get('source'), dict) or os.path.basename(str(old_url)) not in audio.sourceBasenames(ae):
        continue
      if not hasScheme(ae['source'].get('uri')):
        ae['source']['uri'] = enclosure['url']
      if isinstance(enclosure.get('length'), int):
        ae['length'] = enclosure['length']
    changes.append('enclosure url')

  body = post.get('description')
  if body != None and audio.isPlaceholderDescription(ep.get('description')):
    duration = audio.get(ep, 'fileinfo', 'duration')
    text = rss.cleanupHTML(rss.parseDescription(body))
    old_description = ep.get('description')
    ep['description'] = audio.withDuration(text, duration) if duration != None else text
    summary = rss.cleanupHTML(rss.parseSummary(body))
    for ns in ['itunes', 'podcast']:
      if isinstance(ep.get(ns), dict) and 'summary' in ep[ns]:
        if ep[ns]['summary'] == old_description or audio.isPlaceholderDescription(ep[ns]['summary']):
          ep[ns]['summary'] = summary
    changes.append('description')

  if len(changes) > 0:
    log.append(f"{n:03}: post #{post['anchor']} {', '.join(changes)}")
  return len(changes) > 0


def main():
  dry_run = '--dry-run' in sys.argv
  locale.setlocale(locale.LC_TIME, 'C')

  posts = []
  for path in sorted(glob.glob(POSTS_FILES)):
    with open(path) as fp:
      posts.extend(json.load(fp))
  shows = postShows(posts)

  episodes = {}
  for n in range(1, EPISODE_LAST + 1):
    ep = audio.readYAML(f"{EPISODE_DIR}{n:03}.yaml")
    if isinstance(ep, dict) and isinstance(ep.get('fileinfo'), dict) and isinstance(ep.get('podcast'), dict):
      episodes[n] = ep

  holders = {}
  for n, ep in episodes.items():
    ymd = episodeShowDate(ep)
    if ymd != None:
      holders.setdefault(ymd, []).append(n)

  log = []
  skipped = []
  numbering = []
  written = 0
  for ymd, numbers in sorted(holders.items()):
    found = shows.get(ymd, [])
    if len(found) == 0:
      continue
    if len(numbers) > 1:
      skipped.append(f"{ymd}: {', '.join(f'{n:03}' for n in numbers)} hold the same show")
      continue
    if len(found) > 1:
      titled = [p for p in found if re.search(r"(?i)daily\s+[sd]ource\s+code\s+for", str(p.get('title')))]
      if len(titled) != 1:
        skipped.append(f"{ymd}: posts {', '.join(str(p['anchor']) for p in found)} carry the same show")
        continue
      others = [str(p['anchor']) for p in found if p is not titled[0]]
      log.append(f"{numbers[0]:03}: post #{titled[0]['anchor']} is the show, also posted: #{', #'.join(others)}")
      found = titled
    n = numbers[0]
    ep = episodes[n]
    title_date = dateFromTitle(ep.get('title'))
    if title_date != None and title_date != ymd:
      skipped.append(f"{n:03}: title says {title_date}, audio is {ymd}")
      continue
    post_date = dateFromTitle(found[0].get('title'))
    if post_date != None and post_date != ymd:
      skipped.append(f"{n:03}: post #{found[0]['anchor']} title says {post_date}, audio is {ymd}")
      continue
    stated = re.search(r"#\s?(\d{3})\b", str(found[0].get('title')))
    if stated and int(stated.group(1)) != n:
      numbering.append(f"{n:03}: post #{found[0]['anchor']} is titled #{stated.group(1)}")
    if updateEpisode(n, ep, found[0], log):
      written += 1
      if not dry_run:
        audio.writeYAML(f"{EPISODE_DIR}{n:03}.yaml", ep)

  print("\n".join(log))
  print("")
  print(f"Episodes {'to update' if dry_run else 'updated'}: {written}")
  print(f"Skipped ({len(skipped)}):")
  print("\n".join(f"  {s}" for s in skipped))
  print(f"Stated number differs from the episode number ({len(numbering)}):")
  print("\n".join(f"  {s}" for s in numbering))


if __name__ == '__main__':
  main()
