#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import random

import yaml
from collections import defaultdict

SRT_DIR = '../srt/'
SRT_SUFFIX = '.srt'

VTT_DIR = '../vtt/'
VTT_SUFFIX = '.vtt'


def regexify(data):
  data = re.sub(r"\x2e", r"\\x2e", data, flags=re.IGNORECASE)

  return data


def stripEmptyHour(data):
  result = None
  if re.search(r"^00\x3a", data, flags=re.IGNORECASE):
    result = re.sub(r"^00\x3a", "", data, flags=re.IGNORECASE)
  else:
    result = data

  return result

def convertCommaToDecimalPeriod(data):
  return re.sub(r"\x2c", ".", str(data), flags=re.IGNORECASE)


def readSRT(filepath):
  result = None
  f = open(filepath, "r")
  result = f.read()
  return result


def listSRTfiles(filepath):
  result = []
  for dirpath, dirnames, filenames in os.walk(filepath):
    for filename in sorted(filenames):
      if re.search(r"\x2esrt$", filename, flags=re.IGNORECASE):
        result.append(os.path.join(dirpath, filename))

  return sorted(result)

def writeVTT(filepath, contents):
  os.makedirs(os.path.dirname(filepath), exist_ok=True)
  f = open(filepath, "w")
  f.write(contents)
  f.close()
  return

def transformFileName(data):
  re_prefix = regexify(SRT_DIR)
  re_suffix = regexify(SRT_SUFFIX)
  data = re.sub(re_prefix, VTT_DIR, data, flags=re.IGNORECASE)
  data = re.sub(re_suffix, VTT_SUFFIX, data, flags=re.IGNORECASE)
  return data

def parseSRT(srt_data):
  srt_data = re.sub(r"\r\n", "\n", srt_data, flags=re.IGNORECASE)

  srt_dict = { 'data': {}}

  e_elems = None
  e_text = []
  lines = re.split(r"\n", srt_data + "\n", flags=re.IGNORECASE)
  for line in lines:

    if re.search(r"^\s*$", line, flags=re.IGNORECASE):
      if e_elems != None and len(e_text) > 0:
        e_number = len(srt_dict['data']) + 1
        srt_dict['data'][e_number] = {
          'number': e_number,
          'start': e_elems[0],
          'end': e_elems[1],
          'text': " ".join(e_text)
        }
      e_elems = None
      e_text = []
      continue

    if e_elems == None and re.search(r"^(\d{1,})$", line, flags=re.IGNORECASE):
      continue

    if re.search(r"^\d{2}\x3a\d{2}\x3a\d{2}\x2c\d{3}\s\x2d\x2d\x3e\s\d{2}\x3a\d{2}\x3a\d{2}\x2c\d{3}$", line, flags=re.IGNORECASE):
      tp = convertCommaToDecimalPeriod(str(line))
      e_elems = re.split(r"\s\x2d\x2d\x3e\s", tp, flags=re.IGNORECASE)
      continue

    if e_elems != None:
      e_text.append(line.strip())
      continue

  return srt_dict

def renderVTT(data):
  buffer = []

  buffer.append("WEBVTT")
  buffer.append("")

  data_keys = data['data'].keys()

  for k in data_keys:
    obj = data['data'][k]

    timestamps = f"{stripEmptyHour(obj['start'])} --> {stripEmptyHour(obj['end'])}"
    buffer.append(timestamps)

    text_elem = re.split(r"\x20", obj['text'])
    sbuffer = []
    for t in text_elem:
      sbuffer_flat = " ".join(sbuffer)
      if len(sbuffer) > 0 and len(sbuffer_flat) + (len(t) + 1) >= 33:
        buffer.append(sbuffer_flat)
        sbuffer = []
      sbuffer.append(t)

    if len(sbuffer) > 0:
      sbuffer_flat = " ".join(sbuffer)
      buffer.append(sbuffer_flat)

    # Separator for next entry
    buffer.append("")

  return "\n".join(buffer)


def main():
  files = sys.argv[1:] or listSRTfiles(SRT_DIR)
  for srtfile in files:
    vttfile = transformFileName(srtfile)
    print(srtfile, vttfile)


    srt_data = readSRT(srtfile)

    parsed_srt_data = parseSRT(srt_data)
    vtt_data = renderVTT(parsed_srt_data)
    writeVTT(vttfile, vtt_data)


if __name__ == '__main__':
  main()
