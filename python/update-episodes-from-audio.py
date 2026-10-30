#!/usr/bin/python
import os
import re
import sys
import json
import glob
import yaml
import subprocess

AUDIO_DIR = '/media/chrise/work/audio/dsc/DSC/'

EPISODE_DIR = '../yaml/episodes/'
AUDIO_CACHE = '../json/audio-metadata.json'

EPISODE_COUNT = 867

MEDIA_EXTENSIONS = ('.mp3', '.m4v', '.mp4', '.mov')

PLACEHOLDER = '#daily-source-code-'

GENERIC_SUBTITLES = [
  'daily source code',
  'dailysourcecode.com',
  'adam curry: daily source code',
  "adam curry's daily source code",
  'source code',
  'podcast',
]

DURATION_SUFFIX = re.compile(r"\\nDuration: \d{2}:\d{2}:\d{2}$")

ARCHIVE_ALIASES = {
  'DSC-2007-04-17.mp3': '2007/DSC-2007-04-17-repost.mp3',
  'DSC-2009-01-19.mp3': '2009/818 DSC-818-2009-01-2009.mp3',
}


class QuotedDumper(yaml.SafeDumper):
  def analyze_scalar(self, scalar):
    analysis = super().analyze_scalar(scalar.replace("\t", " "))
    analysis.scalar = scalar
    return analysis


def representString(dumper, value):
  if re.match(r"^\d+$", value):
    return dumper.represent_scalar('tag:yaml.org,2002:str', value, style="'")
  if "\n" in value:
    return dumper.represent_scalar('tag:yaml.org,2002:str', value, style='|')
  return dumper.represent_str(value)


def trimLines(text):
  return "\n".join(line.rstrip(" \t\r") for line in text.replace("\r\n", "\n").split("\n"))


QuotedDumper.add_representer(str, representString)


def writeYAML(filepath, contents):
  s = yaml.dump(
    contents,
    Dumper=QuotedDumper,
    indent=2,
    width=1000,
    canonical=False,
    sort_keys=False,
    explicit_start=False,
    default_flow_style=False,
    default_style='',
    allow_unicode=True,
    line_break='\n'
  )
  with open(filepath, "w") as f:
    f.write(s.replace('\n- ', '\n\n- '))


def readYAML(filepath):
  try:
    with open(filepath) as fp:
      return yaml.safe_load(fp.read())
  except (OSError, yaml.YAMLError):
    return None


def readJSON(filepath):
  if os.path.isfile(filepath):
    with open(filepath) as fp:
      return json.load(fp)
  return {}


def writeJSON(filepath, contents):
  with open(filepath, "w") as f:
    json.dump(contents, f, indent=1, ensure_ascii=False, sort_keys=True)
    f.write("\n")


def probe(path):
  out = subprocess.run(
    ['ffprobe', '-v', 'error', '-show_entries',
     'format=duration,size,bit_rate:format_tags:stream=codec_type,codec_name,sample_rate,channels,bit_rate',
     '-of', 'json', path],
    capture_output=True, text=True, check=True
  ).stdout
  return json.loads(out)


def decodeDuration(path):
  out = subprocess.run(
    ['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-map', '0:a:0',
     '-f', 'null', '-', '-progress', 'pipe:1'],
    capture_output=True, text=True
  ).stdout
  found = re.findall(r"^out_time_us=(\d+)$", out, flags=re.MULTILINE)
  if len(found) == 0:
    return None
  return int(found[-1]) / 1000000


def readFrames(path):
  try:
    from mutagen.id3 import ID3, ID3NoHeaderError
  except ImportError:
    return None
  try:
    id3 = ID3(path)
  except ID3NoHeaderError:
    return []
  except Exception as e:
    return [{'error': str(e)}]

  frames = []
  for frame in id3.values():
    entry = {'id': frame.FrameID}
    for attr in ['desc', 'lang', 'owner', 'mime', 'type']:
      value = getattr(frame, attr, None)
      if value not in [None, '']:
        entry[attr] = value if isinstance(value, str) else int(value)
    if hasattr(frame, 'url'):
      entry['url'] = frame.url
    elif hasattr(frame, 'text'):
      entry['text'] = [str(t) for t in frame.text]
    elif hasattr(frame, 'data'):
      entry['size'] = len(frame.data)
    else:
      entry['value'] = str(frame)
    frames.append(entry)
  return frames


def measure(relpath):
  path = os.path.join(AUDIO_DIR, relpath)
  info = probe(path)
  fmt = info.get('format', {})
  audio = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']

  tags = {}
  for k, v in (fmt.get('tags') or {}).items():
    tags[k.lower()] = v

  return {
    'size': int(fmt['size']) if fmt.get('size') else os.path.getsize(path),
    'mtime': int(os.path.getmtime(path)),
    'probe_duration': float(fmt['duration']) if fmt.get('duration') else None,
    'duration': decodeDuration(path),
    'bitrate': int(audio[0]['bit_rate']) if audio and audio[0].get('bit_rate') else None,
    'sample_rate': int(audio[0]['sample_rate']) if audio and audio[0].get('sample_rate') else None,
    'channels': audio[0].get('channels') if audio else None,
    'codec': audio[0].get('codec_name') if audio else None,
    'tags': tags,
    'id3': readFrames(path),
  }


def updateCache(cache):
  changed = False
  for path in sorted(glob.glob(os.path.join(AUDIO_DIR, '**', '*'), recursive=True)):
    if not path.lower().endswith(MEDIA_EXTENSIONS):
      continue
    relpath = os.path.relpath(path, AUDIO_DIR)
    entry = cache.get(relpath)
    if entry != None and entry['size'] == os.path.getsize(path) and entry['mtime'] == int(os.path.getmtime(path)):
      if 'id3' not in entry:
        entry['id3'] = readFrames(path)
        changed = True
      continue
    print(f"Measuring {relpath} ..")
    cache[relpath] = measure(relpath)
    changed = True
  return changed


def get(data, *keys):
  for key in keys:
    if not isinstance(data, dict):
      return None
    data = data.get(key)
  return data


def isSet(value):
  return value != None and str(value).strip() != '' and not str(value).startswith(PLACEHOLDER)


def formatDuration(seconds):
  seconds = int(round(seconds))
  return f"{seconds // 3600:02}:{seconds % 3600 // 60:02}:{seconds % 60:02}"


def dateOf(filename):
  m = re.search(r"(\d{4})-(\d{2})-(\d{2})", str(filename or ''))
  return m.groups() if m else None


def indexArchive(cache):
  index = {}
  for relpath in sorted(cache, key=lambda p: (p.startswith('Misc/'), p)):
    name = os.path.basename(relpath)
    if name not in index:
      index[name] = relpath
    m = re.match(r"^DSC-\d{3}-(\d{4}-\d{2}-\d{2}\.\w+)$", name)
    if m and f"DSC-{m.group(1)}" not in index:
      index[f"DSC-{m.group(1)}"] = relpath
  return index


def findArchiveFile(filename, index, cache):
  if filename == None:
    return None
  if filename in ARCHIVE_ALIASES and ARCHIVE_ALIASES[filename] in cache:
    return ARCHIVE_ALIASES[filename]
  if filename in index:
    return index[filename]
  plain = re.sub(r"^DSC-\d{3}[A-Z]?-(?=\d{4}-)", "DSC-", filename)
  return index.get(plain)


def indexSizes(cache):
  sizes = {}
  for relpath in sorted(cache, key=lambda p: (p.startswith('Misc/'), p)):
    sizes.setdefault(cache[relpath]['size'], []).append(relpath)
  return sizes


def findArchiveFileByLength(ep, relpath, sizes, cache, held):
  length = get(ep, 'enclosure', 'length')
  if not isinstance(length, int) or length < 100000:
    return None
  if relpath != None and cache[relpath]['size'] == length:
    return None
  found = [p for p in sizes.get(length, []) if not p.startswith('Misc/')]
  if len(found) == 1 and found[0] not in held:
    return found[0]
  return None


def findMonthEndFixes(episodes, index):
  fixes = {}
  used = {}
  for n, ep in episodes.items():
    fn = get(ep, 'fileinfo', 'filename')
    if fn:
      used.setdefault(fn, []).append(n)

  for fn, numbers in used.items():
    if len(numbers) < 2:
      continue
    n = min(numbers)
    if isSet(get(episodes[n], 'originalLink')):
      continue
    ymd = dateOf(fn)
    if ymd == None:
      continue
    candidate = f"DSC-{ymd[0]}-{ymd[1]}-{ymd[1]}.mp3"
    if candidate in used or candidate not in index:
      continue
    before = dateOf(get(episodes.get(n - 1), 'fileinfo', 'filename'))
    after = dateOf(get(episodes.get(n + 1), 'fileinfo', 'filename'))
    date = (ymd[0], ymd[1], ymd[1])
    if before != None and before > date:
      continue
    if after != None and after < date:
      continue
    fixes[n] = (fn, candidate)
  return fixes


def subtitleFromTags(tags):
  candidates = [
    tags.get('album'),
    tags.get('tds'),
    tags.get('tt3'),
  ]
  for key in ['tit3', 'tdes']:
    value = tags.get(key)
    if value != None and len(value) <= 120 and '<' not in value:
      candidates.append(value)

  for value in candidates:
    if value == None:
      continue
    value = value.strip()
    if value == '' or value.lower() in GENERIC_SUBTITLES:
      continue
    if re.match(r"^https?://", value):
      continue
    if re.match(r"^(DSC-|#?\d+ )", value):
      continue
    return value
  return None


def isJunkComment(value):
  value = value.strip()
  if re.match(r"^( [0-9A-F]{8})+$", value):
    return True
  if re.match(r"^adam@curry\.com", value):
    return True
  if re.match(r"^Made with ", value):
    return True
  return len(value) < 40


def shownotesFromTags(tags):
  tdes = tags.get('tdes')
  if tdes != None and (len(tdes) > 120 or '<' in tdes):
    return tdes.strip()

  lyrics = tags.get('lyrics-eng')
  if lyrics != None and len(lyrics.strip()) > 40:
    return lyrics.strip()

  comment = tags.get('comment')
  if comment != None and not isJunkComment(comment):
    return comment.strip()

  description = tags.get('description')
  if description != None and len(description.strip()) > 40:
    return description.strip()

  return None


def isPlaceholderDescription(value):
  if value == None:
    return True
  return DURATION_SUFFIX.sub('', str(value)).strip() == ''


def withDuration(text, seconds):
  suffix = f"\\nDuration: {formatDuration(seconds)}"
  if text == None:
    return suffix
  return trimLines(DURATION_SUFFIX.sub('', str(text))).rstrip("\n") + suffix


def titleFor(ymd):
  from datetime import date
  d = date(int(ymd[0]), int(ymd[1]), int(ymd[2]))
  day = d.day
  suffix = 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
  return f"Daily Source Code for {d.strftime('%A')} {d.strftime('%B')} {day}{suffix} {d.year}"


def setMirrored(ep, key, value):
  for ns in ['itunes', 'podcast']:
    if isinstance(ep.get(ns), dict) and (key in ep[ns] or ns == 'itunes'):
      ep[ns][key] = value


def replaceBasename(uri, old, new):
  if uri != None and os.path.basename(str(uri)) == old:
    return str(uri)[:-len(old)] + new
  return uri


def alternateEnclosures(ep):
  value = ep['podcast'].get('alternateEnclosure')
  if isinstance(value, dict):
    uris = get(value, 'source', 'uri')
    entries = []
    for uri in (uris if isinstance(uris, list) else [uris]):
      entry = dict(value, source=dict(value.get('source') or {}, uri=uri))
      if str(entry.get('bitrate')).startswith('None'):
        entry['bitrate'] = None
      entries.append(entry)
    ep['podcast']['alternateEnclosure'] = entries
    value = entries
  return [ae for ae in value or [] if isinstance(ae, dict)]


def sourceBasenames(ae):
  return [os.path.basename(str(get(ae, 'source', 'uri')))]


def updateEpisode(n, ep, audio, relpath, fix, log):
  changes = []
  filename = get(ep, 'fileinfo', 'filename')

  if fix != None:
    old, new = fix
    ymd = dateOf(new)
    title = titleFor(ymd)
    ep['fileinfo']['filename'] = new
    ep['enclosure']['url'] = replaceBasename(get(ep, 'enclosure', 'url'), old, new)
    for ae in alternateEnclosures(ep):
      if isinstance(ae.get('source'), dict):
        ae['source']['uri'] = replaceBasename(ae['source'].get('uri'), old, new)
    ep['pubDate'] = '-'.join(ymd)
    ep['title'] = title
    setMirrored(ep, 'title', title)
    if 'pubDate' in ep['itunes']:
      setMirrored(ep, 'pubDate', ep['pubDate'])
    changes.append(f"file {old} -> {new}")
    filename = new

  duration = audio['duration'] or audio['probe_duration']
  size = audio['size']

  ep['fileinfo']['size'] = size
  ep['fileinfo']['duration'] = int(round(duration))
  ep['fileinfo']['bitrate'] = audio['bitrate']
  ep['fileinfo']['source'] = relpath
  ep['itunes']['duration'] = int(round(duration))

  if os.path.basename(str(get(ep, 'enclosure', 'url'))) == filename:
    ep['enclosure']['length'] = size

  for ae in alternateEnclosures(ep):
    if filename in sourceBasenames(ae):
      ae['length'] = size
      if audio['bitrate'] != None:
        ae['bitrate'] = audio['bitrate']

  old_description = ep.get('description')
  description = old_description
  if fix != None:
    old_description = None
    ep['itunes']['subtitle'] = None
    if 'subtitle' in ep['podcast']:
      ep['podcast']['subtitle'] = None
  if isPlaceholderDescription(old_description):
    shownotes = shownotesFromTags(audio['tags'])
    if shownotes != None:
      changes.append("description from tags")
    description = withDuration(shownotes, duration)
  elif DURATION_SUFFIX.search(str(old_description)):
    description = withDuration(old_description, duration)
  ep['description'] = description
  for ns in ['itunes', 'podcast']:
    if isinstance(ep.get(ns), dict) and 'summary' in ep[ns]:
      if fix != None or ep[ns]['summary'] == old_description or isPlaceholderDescription(ep[ns]['summary']):
        ep[ns]['summary'] = description

  subtitle = subtitleFromTags(audio['tags'])
  if subtitle != None and not isSet(get(ep, 'itunes', 'subtitle')):
    setMirrored(ep, 'subtitle', subtitle)
    changes.append("subtitle from tags")

  if len(changes) > 0:
    log.append(f"{n:03}: {', '.join(changes)}")


def main():
  dry_run = '--dry-run' in sys.argv

  cache = readJSON(AUDIO_CACHE)
  if updateCache(cache):
    writeJSON(AUDIO_CACHE, cache)

  index = indexArchive(cache)
  sizes = indexSizes(cache)

  episodes = {}
  for n in range(1, EPISODE_COUNT + 1):
    if os.path.isfile(f"{EPISODE_DIR}{n:03}.yaml"):
      episodes[n] = readYAML(f"{EPISODE_DIR}{n:03}.yaml")

  fixes = findMonthEndFixes(episodes, index)

  log = []
  missing = []
  skipped = []
  written = 0
  matched = set()
  for n, ep in episodes.items():
    if ep == None:
      skipped.append(f"{n:03}: unreadable yaml")
      continue
    if not isinstance(ep.get('fileinfo'), dict) or not isinstance(ep.get('podcast'), dict):
      skipped.append(f"{n:03}: old stub format, no fileinfo")
      continue

    filename = fixes[n][1] if n in fixes else get(ep, 'fileinfo', 'filename')
    relpath = findArchiveFile(filename, index, cache)
    held = {get(e, 'fileinfo', 'source') for m, e in episodes.items() if m != n and isinstance(e, dict) and isinstance(e.get('fileinfo'), dict)}
    exact = None if n in fixes else findArchiveFileByLength(ep, relpath, sizes, cache, held)
    if exact != None:
      log.append(f"{n:03}: enclosure length matches {exact}, not {relpath or filename}")
      relpath = exact
      ep['fileinfo']['filename'] = os.path.basename(exact)
    if relpath == None:
      missing.append(f"{n:03}: {filename} not in audio archive")
      continue
    matched.add(relpath)

    before = yaml.safe_dump(ep, sort_keys=False)
    updateEpisode(n, ep, cache[relpath], relpath, fixes.get(n), log)
    if yaml.safe_dump(ep, sort_keys=False) != before:
      written += 1
      if not dry_run:
        writeYAML(f"{EPISODE_DIR}{n:03}.yaml", ep)

  unmatched = sorted(p for p in cache if p not in matched and not p.startswith('Misc/'))

  print("\n".join(log))
  print("")
  print(f"Month end file fixes: {len(fixes)}")
  print(f"Episodes {'to update' if dry_run else 'updated'}: {written}")
  print(f"Skipped ({len(skipped)}):")
  print("\n".join(f"  {s}" for s in skipped))
  print(f"Missing in archive ({len(missing)}):")
  print("\n".join(f"  {m}" for m in missing))
  print(f"Archive files not used by any episode ({len(unmatched)}):")
  print("\n".join(f"  {u}" for u in unmatched))


if __name__ == '__main__':
  main()
