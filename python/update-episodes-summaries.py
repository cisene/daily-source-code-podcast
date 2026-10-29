#!/usr/bin/env python3
import os
import re
import sys
import glob
import html
import yaml
import importlib.util
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

RELEASE = '../yaml/release-audio.yaml'
EPISODE_DIR = '../yaml/episodes/'
SHOWNOTES_DIR = '../shownotes/'

BLOCK = {'p', 'div', 'br', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'table', 'blockquote', 'dd', 'dt'}
SKIP = {'script', 'style', 'img'}
DEAD_LINK = re.compile(r"^\s*\[?\s*(mp3|m4a|m4v|mp4|mov|html?|opml|xml|rss|ogg|wma|torrent|download|site|blog|link|here|feed|direct link( to the show)?|show ?notes in opml)\s*\]?\s*$", re.I)
JUNK_LINE = re.compile(r"^[\s,.;:()-]*((\d+[.,]?\d*|approx\.?|about)?\s*(mb|megs?|k|kb|minutes?|mins?|seconds?|hours?|mp3)\b[\s,.;:()-]*)+$|^\s*(production notes|show notes|notes)\s+in\s*[:.]?\s*$", re.I)


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


audio = load('audio', 'update-episodes-from-audio.py')


class Text(HTMLParser):
  def __init__(self):
    super().__init__(convert_charrefs=True)
    self.out, self.skip, self.link = [], 0, None

  def handle_starttag(self, tag, attrs):
    if tag in SKIP:
      self.skip += tag != 'img'
      return
    if tag in BLOCK:
      self.out.append('\n')
    if tag == 'li':
      self.out.append('- ')
    if tag == 'a':
      self.link = []

  def handle_startendtag(self, tag, attrs):
    if tag in BLOCK:
      self.out.append('\n')

  def handle_endtag(self, tag):
    if tag in SKIP:
      self.skip -= tag != 'img' and self.skip > 0
      return
    if tag == 'a' and self.link is not None:
      text = ''.join(self.link)
      self.link = None
      if not DEAD_LINK.match(text):
        self.out.append(text)
      return
    if tag in BLOCK:
      self.out.append('\n')

  def handle_data(self, data):
    if self.skip:
      return
    (self.link if self.link is not None else self.out).append(data)


def htmlText(value):
  value = str(value).replace('\\n', '\n')
  parser = Text()
  parser.feed(value)
  parser.close()
  text = html.unescape(''.join(parser.out))
  text = re.sub(r"<;*/?(s|b|i|u|em|strong|wbr|span|font)\b[^>]*>", '', text, flags=re.I)
  lines = []
  for line in text.split('\n'):
    line = ' '.join(line.split())
    if JUNK_LINE.match(line):
      continue
    if line or (lines and lines[-1]):
      lines.append(line)
  lines = [l for i, l in enumerate(lines)
    if l or not (0 < i < len(lines) - 1 and lines[i - 1].startswith('- ') and lines[i + 1].startswith('- '))]
  return '\n'.join(lines).strip()


def outlineText(path):
  try:
    root = ET.parse(path).getroot()
  except ET.ParseError as err:
    sys.exit(f"{path}: {err}")
  lines = []

  def walk(node, depth):
    for child in node.findall('outline'):
      text = html.unescape(html.unescape(child.get('text') or ''))
      if re.fullmatch(r"\s*</?[A-Za-z][^>]*>\s*", text):
        continue
      text = htmlText(text).replace('\n', ' ').strip()
      if DEAD_LINK.match(text):
        text = ''
      if text:
        lines.append(('  ' * (depth - 1) + '- ' if depth else '') + text)
        walk(child, depth + 1)
      else:
        walk(child, depth)

  body = root.find('body')
  if body is not None:
    walk(body, 0)
  return '\n'.join(lines)


def summary(ep, notes):
  raw = (ep.get('itunes') or {}).get('summary') or ep.get('description') or ''
  post = htmlText(raw)
  if not notes:
    return post or None
  text = outlineText(notes)
  flat = ' '.join(text.split()).lower()
  if post and len(post) <= 400 and ' '.join(post.split()).lower() not in flat:
    return post + '\n\n' + text
  return text or post or None


def main():
  write = '--write' in sys.argv
  only = {a for a in sys.argv[1:] if not a.startswith('--')}
  with open(RELEASE) as fp:
    rows = yaml.safe_load(fp)['audio']
  shownotes = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(f"{SHOWNOTES_DIR}*/*.opml")}

  changed = from_notes = empty = 0
  for row in rows:
    if only and row['episode'] not in only:
      continue
    path = f"{EPISODE_DIR}{row['episode']}.yaml"
    ep = audio.readYAML(path)
    notes = shownotes.get(os.path.splitext(row['release'])[0])
    text = summary(ep, notes)
    from_notes += notes is not None
    empty += text is None
    new = dict(ep)
    new['itunes'] = dict(ep['itunes'], summary=text)
    if (ep.get('podcast') or {}).get('summary') is not None:
      new['podcast'] = dict(ep['podcast'], summary=text)
    if new != ep:
      changed += 1
      if only:
        print(f"== {row['episode']}{' (show notes)' if notes else ''}\n{text}\n")
      if write:
        audio.writeYAML(path, new)
  print(f"{len(only) or len(rows)} episodes: {from_notes} from show notes, {empty} without any text; {changed} changed"
    + ("" if write else " (dry run)"))


if __name__ == '__main__':
  main()
