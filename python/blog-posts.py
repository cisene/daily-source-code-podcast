#!/usr/bin/env python3
import re
import sys
import glob
import json
import html
import email.utils
import xml.etree.ElementTree as ET

STORE = '../json/blog-posts.json'


def text(fragment):
  fragment = re.sub(r'(?is)<(script|style).*?</\1>', ' ', fragment or '')
  fragment = re.sub(r'(?i)<br\s*/?>|</p>|</li>|</div>', '\n', fragment)
  fragment = html.unescape(re.sub(r'<[^>]+>', ' ', fragment))
  return re.sub(r'[ \t\r\f\v]+', ' ', re.sub(r'\n\s*\n+', '\n', fragment)).strip()


def load():
  try:
    with open(STORE) as fp:
      return json.load(fp)
  except (OSError, ValueError):
    return []


def save(posts):
  posts.sort(key=lambda p: (p['date'], p.get('time') or '', p.get('title') or ''))
  with open(STORE, 'w') as fp:
    json.dump(posts, fp, indent=1, ensure_ascii=False)


def key(post):
  return post.get('permalink') or f"{post['date']}|{post.get('title')}"


def merge(posts, new):
  index = {key(p): p for p in posts}
  added = 0
  for p in new:
    if not p['text'] and not p.get('title'):
      continue
    old = index.get(key(p))
    if old is None:
      posts.append(p)
      index[key(p)] = p
      added += 1
    elif len(p['text']) > len(old['text']):
      old.update(p)
  return added


def dateFromLink(link):
  m = re.search(r'/(\d{4})/(\d\d)/(\d\d)', link or '')
  return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None


def feeds():
  new = []
  for path in sorted(glob.glob('../rss/*.xml')):
    try:
      root = ET.parse(path).getroot()
    except ET.ParseError:
      continue
    for item in root.iter('item'):
      link = item.findtext('link') or item.findtext('guid') or ''
      guid = item.findtext('guid') or link
      pub = item.findtext('pubDate')
      date = time = None
      try:
        dt = email.utils.parsedate_to_datetime(pub)
        date, time = dt.strftime('%Y-%m-%d'), dt.strftime('%H:%M:%S %z')
      except (TypeError, ValueError):
        date = dateFromLink(guid) or dateFromLink(link)
      if not date:
        continue
      new.append({'date': date, 'time': time, 'permalink': guid if guid.startswith('http') else link, 'title': (item.findtext('title') or '').strip(), 'text': text(item.findtext('description')), 'source': path[3:]})
  return new


def radioPage(page, url):
  date = dateFromLink(url)
  base = re.sub(r'^https?://web\.archive\.org/web/\d+(id_)?/', '', url).replace(':80/', '/')
  posts = []
  parts = re.split(r'(?i)<a name="(a\d+)"\s*>\s*</a>', page)
  for i in range(1, len(parts) - 1, 2):
    anchor, body = parts[i], parts[i + 1]
    body = re.split(r'(?i)<a href="[^"]*#' + anchor + r'"[^>]*>\s*#?\s*</a>|<!--\s*end of post|<div class="(?:sidebar|footer)', body)[0]
    title = re.search(r'(?is)<(?:div|span) class="(?:title|itemTitle)"[^>]*>(.*?)</(?:div|span)>', body)
    footer = re.search(r'(?is)<font class="small"[^>]*>\s*(\d{1,2}:\d\d:\d\d\s*[AP]M)', body)
    time = footer.group(1) if footer else None
    content = text(body[:footer.start()] if footer else body)
    posts.append({'date': date, 'time': time, 'permalink': f"{base}#{anchor}", 'title': text(title.group(1)) if title else '', 'text': content[:20000], 'source': url})
  return posts


MONTHS = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']


def textDate(s):
  m = re.search(r'(?i)\b(\d{1,2}) (' + '|'.join(MONTHS) + r') (\d{4})', s or '')
  if m:
    return f"{m.group(3)}-{MONTHS.index(m.group(2).lower()) + 1:02}-{int(m.group(1)):02}"
  m = re.search(r'(?i)\b(' + '|'.join(MONTHS) + r') (\d{1,2})(?:st|nd|rd|th)?,? (\d{4})', s or '')
  if m:
    return f"{m.group(3)}-{MONTHS.index(m.group(1).lower()) + 1:02}-{int(m.group(2)):02}"
  return None


def wordpressPage(page, url):
  posted = re.search(r'(?is)Posted on\s*(?:</span>)?(.{0,80}?)</', page)
  date = dateFromLink(url) or textDate(posted.group(1) if posted else None)
  title = re.search(r'(?is)<div class="title"[^>]*>(.*?)</div>', page) or re.search(r'(?is)<title>(.*?)</title>', page)
  body = re.search(r'(?is)class="(?:storycontent|entry|entrytext|post-content)"[^>]*>(.*?)(?:<div id="response"|<div class="(?:postmetadata|feedback|postnavigation)"|<div id="(?:comments|footer)"|<h2[^>]*id="comments"|$)', page)
  if not body:
    body = re.search(r'(?is)<body[^>]*>(.*)</body>', page)
  if not date:
    return []
  base = re.sub(r'^https?://web\.archive\.org/web/\d+(id_)?/', '', url).replace(':80/', '/')
  return [{'date': date, 'time': None, 'permalink': base, 'title': text(title.group(1)) if title else '', 'text': text(body.group(1) if body else page)[:20000], 'source': url}]


def pages(queue):
  new = []
  with open(queue) as fp:
    jobs = [line.split() for line in fp if line.strip()]
  for url, path in jobs:
    try:
      with open(path, encoding='utf-8', errors='replace') as fp:
        page = fp.read()
    except OSError:
      continue
    if 'radio.weblogs.com' in url or re.search(r'curry\.com(:80)?/\d{4}/\d\d/\d\d', url):
      new.extend(radioPage(page, url))
    else:
      new.extend(wordpressPage(page, url))
  return new


def main():
  if len(sys.argv) >= 2 and sys.argv[1] == 'feeds':
    new = feeds()
  elif len(sys.argv) == 3 and sys.argv[1] == 'pages':
    new = pages(sys.argv[2])
  else:
    print('Usage: blog-posts.py feeds | pages QUEUE.txt')
    sys.exit(2)
  posts = load()
  added = merge(posts, new)
  save(posts)
  print(f"{len(new)} posts read, {added} new, {len(posts)} in {STORE[3:]}")


if __name__ == '__main__':
  main()
