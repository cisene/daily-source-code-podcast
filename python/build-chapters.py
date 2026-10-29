#!/usr/bin/env python3
import os
import re
import sys
import json
import math
import glob
from collections import Counter

import html
import numpy as np
import spacy

SRT_DIR = '../srt/'
RELEASE = '../yaml/release-audio.yaml'
EPISODE_DIR = '../yaml/episodes/'
CHAPTERS_DIR = '../chapters/'
BLOCK = 20
WINDOW = 6
MIN_CHAPTER = 150
MIN_MUSIC = 60
MUSIC_GAP = 15

TRANSITIONS = re.compile(
  r"\b(moving on|speaking of|let's go to|let me go to|next up|switching gears|"
  r"on to the|onto the|voicemail|voice mail|anyway|all right|alright|okay so|"
  r"let's talk about|i want to talk about|let's get to|here's|meanwhile|"
  r"back to the|another thing|by the way|now,? )", re.I)

TIME = re.compile(r"(\d\d):(\d\d):(\d\d)[,.](\d{3}) --> (\d\d):(\d\d):(\d\d)[,.](\d{3})")
WORD = re.compile(r"[a-z][a-z']{2,}")


def seconds(h, m, s, ms):
  return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def readSRT(path):
  cues = []
  with open(path, encoding='utf-8', errors='replace') as fp:
    for block in re.split(r"\n\s*\n", fp.read().strip()):
      lines = block.strip().split('\n')
      for i, line in enumerate(lines):
        t = TIME.match(line)
        if t:
          text = ' '.join(l.strip() for l in lines[i + 1:]).strip()
          cues.append((seconds(*t.groups()[:4]), seconds(*t.groups()[4:]), text))
          break
  return cues


def isMusic(text):
  if re.fullmatch(r"\[\s*music\s*\]", text.strip(), flags=re.I):
    return True
  words = re.findall(r"[a-z']+", text.lower())
  return len(words) >= 6 and len(set(words)) / len(words) < 0.35


NOTES_JUNK = re.compile(
  r"(?i)duration:|coupon|discount|donat|subscribe|shownotes|show notes|voicemail|voice mail|"
  r"call anytime|survey|direct link|^link|homepage|official|website|free song|promotional code|% off|\\bcode\\b|"
  r"daily source code for|^#\d+|^from (the )?curry|^dsc-\d|support this show|myspace|downloads?$|^thanks? (to|you)")
STOP = set('the and for with from that this you your are was were have has not but all our out who what when how about into over'.split())


def episodeIndex():
  import yaml
  with open(RELEASE) as fp:
    rows = yaml.safe_load(fp)['audio']
  index = {}
  for row in rows:
    with open(f"{EPISODE_DIR}{row['episode']}.yaml") as fp:
      ep = yaml.safe_load(fp)
    stem, ext = os.path.splitext(os.path.basename(str(row['source'])))
    if not (stem in index and ext.lower() != '.mp3'):
      index[stem] = (ep, row)
    index[os.path.splitext(row['release'])[0]] = (ep, row)
  return index


def episodeNotes(ep):
  if ep is not None:
    notes = re.sub(r"(?i)<br\s*/?>|</p>|</li>|</div>|</tr>", "\n", ep.get('description') or '')
    notes = html.unescape(re.sub(r"<[^>]+>", " ", notes)).replace('\\n', '\n')
    items = []
    for line in notes.split('\n'):
      line = ' '.join(line.split()).strip(' -*')
      if len(line) < 4 or NOTES_JUNK.search(line):
        continue
      words = noteWords(line)
      if words:
        items.append((line, words))
    return items
  return []


def noteTitle(line):
  line = re.sub(r"\.(mp3|m4a|mp4)\b", "", line).replace('_', ' ')
  line = re.sub(r"([a-z])([A-Z][a-z])", r"\1 \2", line) if ' ' not in line.strip() else line
  if isSong(line):
    artist, rest = line.split(' - ', 1)
    head = artist.split()[:2]
    if head:
      again = re.search(r"\s" + re.escape(' '.join(head)) + r"\b", rest)
      if again:
        rest = rest[:again.start()]
    rest = re.sub(r"(?i)\s+(welcome to|official|home of|on|the)\s*$", "", rest.strip())
    line = f"{artist.strip()} - {rest.strip()}"
  line = ' '.join(line.split())
  return line if len(line) <= 70 else line[:67].rsplit(' ', 1)[0] + '...'


def isSong(line):
  if ' - ' not in line or '|' in line or line.count(' - ') > 1:
    return False
  return 1 <= len(line.split(' - ', 1)[0].split()) <= 5


def noteWords(line):
  line = re.sub(r"\.(mp3|m4a|mp4)\b", " ", line)
  line = re.sub(r"([a-z])([A-Z])", r"\1 \2", line.replace('_', ' '))
  return {w for w in re.findall(r"[a-z][a-z']{2,}", line.lower()) if w not in STOP}


def musicStretches(cues):
  spans = []
  for start, end, text in cues:
    if not isMusic(text):
      continue
    if spans and start - spans[-1][1] <= MUSIC_GAP:
      spans[-1][1] = end
    else:
      spans.append([start, end])
  return [(a, b) for a, b in spans if b - a >= MIN_MUSIC]


def documentFrequency():
  df, n = Counter(), 0
  for path in glob.glob(f"{SRT_DIR}*/*.srt"):
    with open(path, encoding='utf-8', errors='replace') as fp:
      words = set(WORD.findall(fp.read().lower()))
    df.update(words)
    n += 1
  return df, n


def cosine(a, b):
  na, nb = np.linalg.norm(a), np.linalg.norm(b)
  return float(a @ b / (na * nb)) if na and nb else 0.0


def bagCosine(a, b):
  common = set(a) & set(b)
  num = sum(a[w] * b[w] for w in common)
  den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
  return num / den if den else 0.0


def segmentSpeech(nlp, cues, start, end, df, ndocs):
  inside = [c for c in cues if c[0] >= start and c[0] < end and not isMusic(c[2]) and c[2]]
  if not inside or end - start < 2 * MIN_CHAPTER:
    return []
  blocks = []
  t = start
  while t < end:
    texts = [c[2] for c in inside if t <= c[0] < t + BLOCK]
    blocks.append((t, ' '.join(texts)))
    t += BLOCK
  docs = list(nlp.pipe([b[1] for b in blocks]))
  bags, vecs = [], []
  for doc in docs:
    lemmas = [tok.lemma_.lower() for tok in doc
      if tok.is_alpha and not tok.is_stop and tok.pos_ in ('NOUN', 'PROPN', 'VERB', 'ADJ') and len(tok) > 2]
    bags.append(Counter({w: c * math.log(ndocs / (1 + df.get(w, 0))) for w, c in Counter(lemmas).items()}))
    content = [tok.vector for tok in doc if tok.has_vector and not tok.is_stop and tok.is_alpha]
    vecs.append(np.mean(content, axis=0) if content else np.zeros(nlp.vocab.vectors_length))
  scores = []
  for i in range(1, len(blocks)):
    left, right = range(max(0, i - WINDOW), i), range(i, min(len(blocks), i + WINDOW))
    lb, rb = Counter(), Counter()
    for j in left:
      lb.update(bags[j])
    for j in right:
      rb.update(bags[j])
    lv = np.mean([vecs[j] for j in left], axis=0)
    rv = np.mean([vecs[j] for j in right], axis=0)
    scores.append(0.6 * bagCosine(lb, rb) + 0.4 * cosine(lv, rv))
  if not scores:
    return []
  depth = []
  for i, s in enumerate(scores):
    lpeak = max(scores[:i + 1])
    rpeak = max(scores[i:])
    d = (lpeak - s) + (rpeak - s)
    gap_start = blocks[i + 1][0]
    first = next((c for c in inside if c[0] >= gap_start - 5), None)
    if first and TRANSITIONS.search(first[2][:60]):
      d *= 1.3
    depth.append((d, gap_start))
  values = np.array([d for d, _ in depth])
  cutoff = values.mean() + 0.5 * values.std()
  chosen = []
  for d, t in sorted(depth, reverse=True):
    if d < cutoff:
      break
    if t - start < MIN_CHAPTER or end - t < MIN_CHAPTER:
      continue
    if all(abs(t - c) >= MIN_CHAPTER for c in chosen):
      chosen.append(t)
  snapped = []
  for t in sorted(chosen):
    near = [c for c in inside if abs(c[0] - t) <= 15]
    best, gap = t, -1
    for k, c in enumerate(inside):
      if c in near and k > 0 and c[0] - inside[k - 1][1] > gap:
        best, gap = c[0], c[0] - inside[k - 1][1]
    snapped.append(round(best))
  return snapped


def title(nlp, text, df, ndocs, used):
  doc = nlp(text[:100000])
  ents = Counter(e.text.strip() for e in doc.ents
    if e.label_ in ('PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'NORP', 'LOC', 'FAC')
    and len(e.text.strip()) > 2 and e.text.lower() not in ('adam', 'adam curry', 'curry'))
  words = Counter(tok.lemma_.lower() for tok in doc
    if tok.is_alpha and not tok.is_stop and tok.pos_ in ('NOUN', 'PROPN') and len(tok) > 3)
  scored = sorted(((c * math.log(ndocs / (1 + df.get(w, 0))), w) for w, c in words.items() if c >= 2), reverse=True)
  parts = [e for e, c in ents.most_common(6) if c >= 2 and e not in used][:3]
  for _, w in scored:
    if len(parts) >= 2:
      break
    if not any(w in p.lower() for p in parts):
      parts.append(w)
  used.update(parts)
  return ', '.join(p if p[:1].isupper() else p.capitalize() for p in parts) if parts else 'Talk'


def draft(nlp, path, df, ndocs, ep=None):
  cues = readSRT(path)
  if not cues:
    return None
  end = cues[-1][1]
  music = musicStretches(cues)
  bounds, t = [], 0.0
  for a, b in music:
    if a > t:
      bounds.append(('talk', t, a))
    bounds.append(('music', a, b))
    t = b
  if t < end:
    bounds.append(('talk', t, end))
  chapters = []
  for kind, a, b in bounds:
    if kind == 'music':
      chapters.append({'startTime': round(a), 'kind': 'music'})
      continue
    starts = [round(a)] + segmentSpeech(nlp, cues, a, b, df, ndocs)
    for s in starts:
      chapters.append({'startTime': s, 'kind': 'talk'})
  merged = []
  for i, ch in enumerate(chapters):
    nxt = chapters[i + 1]['startTime'] if i + 1 < len(chapters) else end
    if merged and ch['kind'] == 'talk' and nxt - ch['startTime'] < (45 if merged[-1]['kind'] == 'music' else 60):
      continue
    if merged and ch['kind'] == 'music' and merged[-1]['kind'] == 'music':
      continue
    merged.append(ch)
  notes = episodeNotes(ep)
  windows = []
  for i, ch in enumerate(merged):
    nxt = merged[i + 1]['startTime'] if i + 1 < len(merged) else end
    pad = 90 if ch['kind'] == 'music' else 0
    words = set(re.findall(r"[a-z][a-z']{2,}", ' '.join(
      c[2] for c in cues if ch['startTime'] - pad <= c[0] < nxt + pad).lower()))
    windows.append(words)
  pointer = 0
  for line, words in notes:
    best, score = None, 0.0
    for i in range(pointer, len(merged)):
      found = words & windows[i]
      value = sum(math.log(ndocs / (1 + df.get(w, 0))) for w in found)
      if (len(found) >= 2 or any(len(w) >= 6 and df.get(w, 0) < ndocs / 20 for w in found)) and value > score:
        best, score = i, value
    if best is not None:
      if isSong(line) and merged[best]['kind'] == 'talk' and best + 1 < len(merged) \
          and merged[best + 1]['kind'] == 'music' and not merged[best + 1].get('notes'):
        best += 1
      shown = noteTitle(line)
      before = merged[best].get('notes', [])
      if any(noteWords(shown) <= noteWords(b) or noteWords(b) <= noteWords(shown) for b in before):
        pointer = best
        continue
      merged[best].setdefault('notes', []).append(shown)
      merged[best].setdefault('lines', []).append(line)
      pointer = best
  songs = [line for line, _ in notes if isSong(line)]
  placed = {l for ch in merged for l in ch.get('lines', [])}
  anchors = [(-1, -1)] + [(k, i) for k, line in enumerate(songs) for i, ch in enumerate(merged) if line in ch.get('lines', [])] + [(len(songs), len(merged))]
  for (k0, i0), (k1, i1) in zip(anchors, anchors[1:]):
    missing = [l for l in songs[k0 + 1:k1] if l not in placed]
    empty = [i for i in range(i0 + 1, i1) if merged[i]['kind'] == 'music' and not merged[i].get('notes')]
    if missing and len(missing) == len(empty):
      for line, i in zip(missing, empty):
        merged[i]['notes'] = [noteTitle(line)]
        merged[i]['guess'] = True
  used = set()
  for i, ch in enumerate(merged):
    nxt = merged[i + 1]['startTime'] if i + 1 < len(merged) else end
    text = ' '.join(c[2] for c in cues if ch['startTime'] <= c[0] < nxt and not isMusic(c[2]))
    ch['end'] = round(nxt)
    ch['first'] = text[:110]
    if ch.get('notes'):
      ch['title'] = ('Music: ' if ch['kind'] == 'music' else '') + ' / '.join(ch['notes'][:2])
    elif ch['kind'] == 'music':
      ch['title'] = 'Music'
    elif i == 0:
      ch['title'] = 'Intro' if nxt - ch['startTime'] < 120 else 'Intro: ' + title(nlp, text, df, ndocs, used)
    else:
      ch['title'] = title(nlp, text, df, ndocs, used)
  return merged, end


def clock(s):
  return f"{int(s // 3600)}:{int(s % 3600 // 60):02}:{int(s % 60):02}"


def chaptersFile(chapters, end, ep, row):
  out = {
    'version': '1.2.0',
    'author': 'Adam Curry',
    'title': ep.get('title'),
    'podcastName': 'Daily Source Code',
    'fileName': row['release'],
    'chapters': [],
  }
  for c in chapters:
    out['chapters'].append({'startTime': int(c['startTime']), 'endTime': int(c['end']), 'title': c['title']})
  return out


def main():
  write = '--write' in sys.argv
  args = [a for a in sys.argv[1:] if a != '--write']
  if write:
    files = args or sorted(glob.glob(f"{SRT_DIR}*/*.srt"))
  else:
    outdir, files = args[0], args[1:]
    os.makedirs(outdir, exist_ok=True)
  nlp = spacy.load('en_core_web_lg', disable=['parser'])
  nlp.max_length = 2000000
  df, ndocs = documentFrequency()
  index = episodeIndex()
  done, skipped = 0, []
  for path in files:
    base = os.path.splitext(os.path.basename(path))[0]
    ep, row = index.get(base, (None, None))
    if write and ep is None:
      skipped.append(path)
      continue
    result = draft(nlp, path, df, ndocs, ep)
    if result is None:
      print(f"{path}: no cues")
      continue
    chapters, end = result
    if write:
      year = os.path.basename(os.path.dirname(path))
      target = f"{CHAPTERS_DIR}{year}/{os.path.splitext(row['release'])[0]}.json"
      os.makedirs(os.path.dirname(target), exist_ok=True)
      with open(target, 'w') as fp:
        json.dump(chaptersFile(chapters, end, ep, row), fp, indent=2, ensure_ascii=False)
        fp.write('\n')
      done += 1
      print(f"{target}: {len(chapters)} chapters over {clock(end)}", flush=True)
      continue
    with open(f"{outdir}/{base}.json", 'w') as fp:
      json.dump({'version': '1.2.0', 'chapters': [
        {'startTime': c['startTime'], 'title': c['title']} for c in chapters]}, fp, indent=2, ensure_ascii=False)
    with open(f"{outdir}/{base}.txt", 'w') as fp:
      fp.write(f"{base}  ({clock(end)}, {len(chapters)} chapters)\n\n")
      for c in chapters:
        fp.write(f"{clock(c['startTime'])} - {clock(c['end'])}  {c['title']}{'  (by order)' if c.get('guess') else ''}\n    \"{c['first']}\"\n")
    print(f"{base}: {len(chapters)} chapters over {clock(end)}")
  if write:
    for path in skipped:
      print(f"no episode: {path}")
    print(f"{done} chapter files, {len(skipped)} transcripts without an episode")


if __name__ == '__main__':
  main()
