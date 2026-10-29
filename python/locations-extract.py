#!/usr/bin/env python3
import re
import sys
import glob
import json
import html
import spacy
import xml.etree.ElementTree as ET

LABELS = ['GPE', 'LOC', 'FAC']
VENUE = re.compile(r"\b(hotel|motel|inn|hostel|resort|lodge|airport|airfield|terminal|station|cent(er|re)|convention|expo|arena|stadium|theat(er|re)|hall|club|bar|pub|caf[eé]|restaurant|lounge|starbucks|mall|plaza|square|park|cathedral|church|museum|university|college|campus|studios?|tower|palace|castle|bridge|harbou?r|pier|marina|beach|campground|base|hospital|hilton|marriott|sheraton|hyatt|westin|ritz|four seasons|waldorf|holiday inn|best western|radisson|novotel|crowne plaza|intercontinental)\b", re.I)
TS = re.compile(r'^\d+$|-->')


def srtText(path):
  with open(path, encoding='utf-8', errors='replace') as fp:
    lines = [l.strip() for l in fp if l.strip() and not TS.search(l.strip())]
  return ' '.join(l for l in lines if l != '[ Music ]')


def stripHTML(text):
  return html.unescape(re.sub(r'<[^>]+>', ' ', text or ''))


def opmlText(path):
  try:
    root = ET.parse(path).getroot()
  except ET.ParseError:
    return ''
  return '\n'.join(stripHTML(o.get('text')) for o in root.iter('outline') if o.get('text'))


def descriptionText(path):
  import yaml
  try:
    with open(path) as fp:
      ep = yaml.safe_load(fp)
  except Exception:
    return ''
  if not isinstance(ep, dict) or not isinstance(ep.get('description'), str) or ep['description'].startswith('#'):
    return ''
  return stripHTML(ep['description'].replace('\\n', '\n'))


def sources():
  for path in sorted(glob.glob('../srt/*/*.srt')):
    yield path[3:], srtText(path)
  for path in sorted(glob.glob('../shownotes/*/*.opml')):
    yield path[3:], opmlText(path)
  for path in sorted(glob.glob('../yaml/episodes/[0-9]*.yaml')):
    yield path[3:], descriptionText(path)


def clean(name):
  name = re.sub(r"^(the|downtown|beautiful|sunny|lovely)\s+", '', name.strip(), flags=re.I)
  name = re.sub(r"('s|’s)$", '', name)
  return re.sub(r'\s+', ' ', name).strip(' .,;:!?"\'()[]')


def main():
  nlp = spacy.load('en_core_web_lg', disable=['parser', 'lemmatizer', 'tagger', 'attribute_ruler'])
  nlp.max_length = 5_000_000
  found = {}
  docs = ((text, name) for name, text in sources() if text.strip())
  for doc, name in nlp.pipe(docs, as_tuples=True, batch_size=4, n_process=4):
    for ent in doc.ents:
      if ent.label_ not in LABELS and not (ent.label_ == 'ORG' and VENUE.search(ent.text)):
        continue
      key = clean(ent.text)
      if len(key) < 2 or not re.search(r'[A-Za-z]', key):
        continue
      entry = found.setdefault(key, {'files': {}})
      entry[ent.label_] = entry.get(ent.label_, 0) + 1
      entry['files'][name] = entry['files'].get(name, 0) + 1
    print(name, file=sys.stderr)
  with open(sys.argv[1], 'w') as fp:
    json.dump(found, fp, indent=1, ensure_ascii=False)
  print(f"{len(found)} names", file=sys.stderr)


if __name__ == '__main__':
  main()
