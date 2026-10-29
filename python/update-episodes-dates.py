#!/usr/bin/env python3
import re
import sys
import glob
import importlib.util
from datetime import datetime
from email.utils import format_datetime, parsedate_to_datetime

EPISODE_DIR = '../yaml/episodes/'
RFC822 = re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4} \d{2}:\d{2}:\d{2} [+-]\d{4}$")


def load(name, filename):
  spec = importlib.util.spec_from_file_location(name, filename)
  mod = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(mod)
  return mod


audio = load('audio', 'update-episodes-from-audio.py')


def parse(value):
  text = re.sub(r"\s+", ' ', str(value).strip())
  try:
    return datetime.strptime(text, '%a %b %d %H:%M:%S %Y %z'), text[:3]
  except ValueError:
    pass
  dt = parsedate_to_datetime(text)
  if dt is None or dt.tzinfo is None:
    raise ValueError(f"no time zone: {value!r}")
  given = re.match(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", text)
  return dt, given.group(1) if given else None


def main():
  write = '--write' in sys.argv
  changed, values, problems = 0, 0, []
  paths = sorted(glob.glob(f"{EPISODE_DIR}*.yaml"))
  for path in paths:
    ep = audio.readYAML(path)
    name = path.split('/')[-1]
    new = dict(ep)
    for where in (None, 'itunes', 'podcast'):
      holder = new if where is None else new.get(where)
      if not isinstance(holder, dict) or holder.get('pubDate') is None:
        continue
      value = holder['pubDate']
      try:
        dt, given = parse(value)
      except (TypeError, ValueError) as err:
        problems.append(f"{name} {where or 'item'}: cannot read {value!r} ({err})")
        continue
      if given and given != dt.strftime('%a'):
        problems.append(f"{name} {where or 'item'}: {value!r} says {given}, the date is a {dt.strftime('%a')}")
      rfc = format_datetime(dt)
      if not RFC822.match(rfc):
        problems.append(f"{name}: {rfc!r} is not RFC 822")
        continue
      values += 1
      if rfc != value:
        if where is None:
          new['pubDate'] = rfc
        else:
          new[where] = dict(holder, pubDate=rfc)
    if new != ep:
      changed += 1
      if write:
        audio.writeYAML(path, new)
  for line in problems:
    print(line)
  print(f"{len(paths)} episodes, {values} dates valid RFC 822, {changed} changed, {len(problems)} problems"
    + ("" if write else " (dry run)"))
  if problems:
    sys.exit(1)


if __name__ == '__main__':
  main()
