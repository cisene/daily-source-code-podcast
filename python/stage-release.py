#!/usr/bin/env python3
import os
import re
import sys
import glob
import shutil
import subprocess
import unicodedata
import yaml
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3

UPLOAD = '../yaml/upload.yaml'
RELEASE = '../yaml/release-audio.yaml'
REPO = '../'
AUDIO_DIR = '/media/chrise/work/audio/dsc/DSC/'
PICTURE = '../artwork/episode-300x300.png'
CHANNEL = '../yaml/daily-source-code.yaml'
EPISODE_DIR = '../yaml/episodes/'
ARTIST = 'Adam Curry'
GENRE = 'Podcast'
GENRE_V1 = 186
INNER_ID3 = re.compile(rb'(ID3|3DI)[\x02-\x04]\x00[\x00-\xff][\x00-\x7f]{4}[A-Z][A-Z0-9]{2}')
SRT_DIR = '../srt/'
VTT_DIR = '../vtt/'
CHAPTERS_DIR = '../chapters/'
SHOWNOTES_DIR = '../shownotes/'
PARTS = ['media', 'srt', 'vtt', 'chapters', 'opml']
SPACE_MARGIN = 2 * 1024 ** 3
VIDEO = ('.m4v', '.mp4')


def sourcePath(source):
  return REPO + source if source.startswith('mp3/') else AUDIO_DIR + source


def upToDate(dest, *sources):
  return os.path.exists(dest) and all(os.path.getmtime(dest) >= os.path.getmtime(s) for s in sources)


def audioMD5(path):
  out = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-map', '0:a', '-c', 'copy', '-f', 'md5', '-'],
    capture_output=True, text=True)
  return out.stdout.strip() if out.returncode == 0 else None


def guard(dest):
  real = os.path.realpath(dest)
  for root in (AUDIO_DIR, REPO + 'mp3'):
    root = os.path.realpath(root)
    if real == root or real.startswith(root + os.sep):
      sys.exit(f"refused: {dest} is inside {root}")


def wantedTags(row, ep, album):
  tags = {'TIT2': str(ep['title']).strip(), 'TPE1': ARTIST, 'TALB': album, 'TDRC': str(row['date']), 'TCON': GENRE}
  if str(row['episode']).isdigit():
    tags['TRCK'] = str(int(row['episode']))
  return tags


def probe(path):
  out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
    'stream=codec_name,sample_rate:format=duration', '-of', 'json', path], capture_output=True, text=True)
  if out.returncode != 0:
    return None, out.stderr.strip()
  import json
  data = json.loads(out.stdout)
  stream = (data.get('streams') or [{}])[0]
  return (stream.get('codec_name'), stream.get('sample_rate'), float(data['format']['duration'])), out.stderr.strip()


def packetSeconds(path):
  out = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-map', '0:a', '-c', 'copy',
    '-f', 'null', '-progress', 'pipe:1', '-'], capture_output=True, text=True)
  times = [l.split('=', 1)[1] for l in out.stdout.splitlines() if l.startswith('out_time_us=')]
  return int(times[-1]) / 1e6 if out.returncode == 0 and times and times[-1].isdigit() else None


def latin1(text, size):
  out = ''
  for ch in text:
    try:
      ch.encode('latin-1')
    except UnicodeEncodeError:
      ch = unicodedata.normalize('NFKD', ch).encode('latin-1', 'ignore').decode('latin-1') or '?'
    out += ch
  return out.encode('latin-1')[:size].ljust(size, b'\0')


def id3v1(tags):
  return (b'TAG' + latin1(tags['TIT2'], 30) + latin1(tags['TPE1'], 30) + bytes(30)
    + latin1(tags['TDRC'][:4], 4) + bytes(30) + bytes([GENRE_V1]))


def tagged(path, tags):
  if (tagsOf(path) or (None, None))[1] != tags:
    return False
  with open(path, 'rb') as fp:
    fp.seek(max(0, os.path.getsize(path) - 128))
    return fp.read() == id3v1(tags)


def tagsOf(path):
  try:
    id3 = ID3(path, load_v1=False)
  except ID3NoHeaderError:
    return None
  texts = {k: str(v) for k, v in id3.items() if not k.startswith('APIC')}
  return id3.version, texts, id3.getall('APIC')


def verifyMP3(src, path, tags, picture):
  tag = tagsOf(path)
  if tag is None:
    return 'no ID3v2 tag'
  version, texts, pictures = tag
  if version != (2, 4, 0):
    return f"ID3 version {version}"
  if texts != tags:
    return f"tags {texts} != {tags}"
  if len(pictures) != 1:
    return f"{len(pictures)} pictures"
  pic = pictures[0]
  if pic.mime != 'image/png' or pic.type != 3 or pic.data != picture:
    return f"picture wrong ({pic.mime}, type {pic.type}, {len(pic.data)} bytes)"
  with open(path, 'rb') as fp:
    fp.seek(max(0, os.path.getsize(path) - 65536))
    tail = fp.read()
  if tail[-128:].startswith(b'TAG') or b'APETAGEX' in tail:
    return 'an old ID3v1 or APE tag is left'
  with open(path, 'rb') as fp:
    data = fp.read()
  inner = [m.start() for m in INNER_ID3.finditer(data, 1)] + [m.start() for m in re.finditer(rb'LYRICSBEGIN', data)]
  if inner:
    return f"an old tag inside the file at {inner[:5]}"
  (got, err), (had, _) = probe(path), probe(src)
  if got is None or err:
    return f"ffprobe: {err[:200]}"
  seconds = packetSeconds(path)
  if had is None or got[:2] != had[:2] or seconds is None or abs(got[2] - seconds) > 0.5:
    return f"stream {got} (packets {seconds} s) != source {had[:2] if had else None}"
  try:
    MP3(path)
  except Exception as e:
    return f"mutagen cannot read the mp3: {e}"
  before, after = audioMD5(src), audioMD5(path)
  if before is None or before != after:
    return f"audio differs after the copy ({before} / {after})"
  return None


def tagSpans(data):
  spans = []
  for m in INNER_ID3.finditer(data, 1):
    b = data[m.start() + 6:m.start() + 10]
    size = (b[0] << 21) | (b[1] << 14) | (b[2] << 7) | b[3]
    footer = 10 if data[m.start() + 5] & 0x10 else 0
    spans.append((m.start(), min(len(data), m.start() + 10 + size + footer)))
  if len(data) >= 128 and data[-128:-125] == b'TAG':
    spans.append((len(data) - 128, len(data)))
  return spans


def cleanSource(src, dest):
  with open(src, 'rb') as fp:
    data = fp.read()
  spans = tagSpans(data)
  if not spans:
    return src, None, []
  clean = dest + '.src'
  guard(clean)
  with open(clean, 'wb') as fp:
    at = 0
    for start, end in spans:
      fp.write(data[at:start])
      at = end
    fp.write(data[at:])
  if os.path.getsize(clean) != len(data) - sum(e - s for s, e in spans):
    os.remove(clean)
    sys.exit(f"could not read {src}")
  return clean, clean, spans


def releaseMP3(src, dest, tags, picture):
  guard(dest)
  tmp = dest + '.part'
  guard(tmp)
  source, clean, _ = cleanSource(src, dest)
  try:
    return encodeMP3(source, tmp, dest, tags, picture)
  finally:
    if clean and os.path.exists(clean):
      os.remove(clean)


def encodeMP3(src, tmp, dest, tags, picture):
  command = ['nice', '-n', '10', 'ffmpeg', '-nostdin', '-v', 'error', '-y', '-i', src, '-i', PICTURE,
    '-map', '0:a', '-map', '1:v', '-c', 'copy', '-map_metadata', '-1', '-map_chapters', '-1',
    '-fflags', '+bitexact', '-flags', '+bitexact', '-id3v2_version', '4', '-write_id3v1', '0',
    '-metadata:s:v', 'title=Cover (front)', '-metadata:s:v', 'comment=Cover (front)',
    '-disposition:v', 'attached_pic']
  for key, frame in (('title', 'TIT2'), ('artist', 'TPE1'), ('album', 'TALB'), ('date', 'TDRC'), ('genre', 'TCON'), ('track', 'TRCK')):
    if frame in tags:
      command += ['-metadata', f"{key}={tags[frame]}"]
  command += ['-f', 'mp3', tmp]
  run = subprocess.run(command, capture_output=True, text=True)
  if run.returncode != 0:
    if os.path.exists(tmp):
      os.remove(tmp)
    return f"ffmpeg failed: {run.stderr.strip()[:200]}"
  error = verifyMP3(src, tmp, tags, picture)
  if not error:
    size, v1 = os.path.getsize(tmp), id3v1(tags)
    with open(tmp, 'ab') as fp:
      fp.write(v1)
    with open(tmp, 'rb') as fp:
      fp.seek(size)
      if os.path.getsize(tmp) != size + 128 or fp.read() != v1:
        error = 'ID3v1 not written'
    if not error and (tagsOf(tmp) or (None, None))[1] != tags:
      error = 'the ID3v2 tag changed with the ID3v1'
  if error:
    os.remove(tmp)
    return error
  os.replace(tmp, dest)
  return None


def copyFile(src, dest):
  guard(dest)
  os.makedirs(os.path.dirname(dest), exist_ok=True)
  tmp = dest + '.part'
  shutil.copyfile(src, tmp)
  os.replace(tmp, dest)


def mediaFolder(release):
  return 'video' if release.lower().endswith(VIDEO) else 'audio'


def stageMedia(rows, stage, write):
  with open(CHANNEL) as fp:
    album = next(str(t['text']) for t in yaml.safe_load(fp)['rss']['channel']['tags']
      if t['tag'] == 'title' and not t.get('namespace'))
  with open(PICTURE, 'rb') as fp:
    picture = fp.read()
  todo = []
  for row in rows:
    src = sourcePath(str(row['source']))
    dest = os.path.join(stage, mediaFolder(row['release']), row['release'])
    tags = None
    if row['release'].endswith('.mp3'):
      with open(f"{EPISODE_DIR}{row['episode']}.yaml") as fp:
        tags = wantedTags(row, yaml.safe_load(fp), album)
    deps = [src, PICTURE] if tags else [src]
    if not os.path.exists(src):
      print(f"no source: {row['episode']} {src}")
    elif not upToDate(dest, *deps) or (tags and not tagged(dest, tags)):
      todo.append((row, src, dest, tags))
  need = sum(os.path.getsize(src) for _, src, _, _ in todo)
  free = shutil.disk_usage(stage if os.path.exists(stage) else os.path.dirname(stage)).free
  print(f"media: {len(rows)} releases, {len(todo)} to stage, {need / 1e9:.1f} GB, {free / 1e9:.0f} GB free")
  if need + SPACE_MARGIN > free:
    sys.exit("not enough free space")
  if write:
    failed = []
    for i, (row, src, dest, tags) in enumerate(todo, 1):
      os.makedirs(os.path.dirname(dest), exist_ok=True)
      error = releaseMP3(src, dest, tags, picture) if tags else copyFile(src, dest)
      if error:
        failed.append(f"{row['release']}: {error}")
      print(f"[{i}/{len(todo)}] {row['release']}" + (f" FAILED {error}" if error else ''), flush=True)
    for line in failed:
      print(f"failed: {line}")
  return {os.path.join(mediaFolder(r['release']), r['release']) for r in rows}


def transcriptIndex(rows):
  index = {}
  for row in rows:
    stem, ext = os.path.splitext(os.path.basename(str(row['source'])))
    release = os.path.splitext(row['release'])[0]
    if stem not in index or ext.lower() == '.mp3':
      index[stem] = release
    index[release] = release
  return index


def stageFiles(part, pairs, stage, write):
  wanted, copied = set(), 0
  for src, rel in pairs:
    if rel in wanted:
      print(f"{part}: two sources for {rel}: {src}")
      continue
    wanted.add(rel)
    dest = os.path.join(stage, rel)
    if not upToDate(dest, src):
      copied += 1
      if write:
        copyFile(src, dest)
  print(f"{part}: {len(wanted)} files, {copied} to copy")
  return wanted


def transcriptPairs(rows, base, ext, folder):
  index = transcriptIndex(rows)
  pairs = []
  for path in sorted(glob.glob(f"{base}*/*{ext}")):
    release = index.get(os.path.splitext(os.path.basename(path))[0])
    if release is None:
      print(f"{folder}: no release for {os.path.relpath(path, REPO)}")
      continue
    pairs.append((path, os.path.join(folder, release + ext)))
  return pairs


def main():
  write = '--write' in sys.argv
  parts = [a for a in sys.argv[1:] if not a.startswith('--')] or PARTS
  for part in parts:
    if part not in PARTS:
      sys.exit(f"unknown part {part} (known: {', '.join(PARTS)})")
  with open(UPLOAD) as fp:
    stage = yaml.safe_load(fp).get('stage')
  if not stage:
    sys.exit(f"no stage in {UPLOAD}")
  with open(RELEASE) as fp:
    rows = yaml.safe_load(fp)['audio']
  if write:
    guard(os.path.join(stage, 'x'))
    os.makedirs(stage, exist_ok=True)

  expected = {}
  if 'media' in parts:
    names = stageMedia(rows, stage, write)
    expected['audio'] = {n for n in names if n.startswith('audio/')}
    expected['video'] = {n for n in names if n.startswith('video/')}
  if 'srt' in parts:
    expected['srt'] = stageFiles('srt', transcriptPairs(rows, SRT_DIR, '.srt', 'srt'), stage, write)
  if 'vtt' in parts:
    expected['vtt'] = stageFiles('vtt', transcriptPairs(rows, VTT_DIR, '.vtt', 'vtt'), stage, write)
  if 'chapters' in parts:
    pairs = [(p, os.path.join('chapters', os.path.basename(p))) for p in sorted(glob.glob(f"{CHAPTERS_DIR}*/*.json"))]
    expected['chapters'] = stageFiles('chapters', pairs, stage, write)
  if 'opml' in parts:
    pairs = [(p, os.path.join('opml', os.path.basename(p))) for p in sorted(glob.glob(f"{SHOWNOTES_DIR}*/*.opml"))]
    expected['opml'] = stageFiles('opml', pairs, stage, write)

  prune = write and '--prune' in sys.argv
  for folder, names in expected.items():
    for path in sorted(glob.glob(os.path.join(stage, folder, '**', '*'), recursive=True)):
      rel = os.path.relpath(path, stage)
      if os.path.isfile(path) and rel not in names:
        print(f"not a release file: {rel}" + (' (removed)' if prune else ''))
        if prune:
          os.remove(path)
  if not write:
    print('dry run (add --write)')


if __name__ == '__main__':
  main()
