#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

import glob

#import sounddevice as sd
#import numpy as np
#import whisper
#import queue
#import threading

MP3_DIR = '/media/chrise/work/audio/dsc/DSC/2004/'

SRT_DIR = '/media/chrise/work/repos/github/cisene/daily-source-code-podcast/srt/{year}/'

CMD_WHISPER = [
  'whisper',
  '--verbose False',
  '--task transcribe',
  '--model tiny',
  '--output_dir {srt_dir}',
  '--output_format srt',
  '--language en',
  '{fullpath_mp3}',
]

def extractFilename(filepath):
  filepath = re.sub(r"^.*\x2f", "", str(filepath), flags=re.IGNORECASE)
  filepath = re.sub(r"\x2e.*$", "", str(filepath), flags=re.IGNORECASE)
  return filepath

def listMP3files(filepath):
  result = []
  #print(f"filepath: '{filepath}'")

  for filename in sorted(glob.glob(filepath, recursive = True)):
    if filename != None:
      if re.search(r"\x2emp3$", str(filename), flags=re.IGNORECASE):
        if filename not in result:
          result.append(filename)

  return result

def main():
  dir_list = [
    '/media/chrise/work/audio/dsc/DSC/2004/*',
    '/media/chrise/work/audio/dsc/DSC/2005/*',
    '/media/chrise/work/audio/dsc/DSC/2006/*',
    '/media/chrise/work/audio/dsc/DSC/2007/*',
    '/media/chrise/work/audio/dsc/DSC/2008/*',
    '/media/chrise/work/audio/dsc/DSC/2009/*',
    '/media/chrise/work/audio/dsc/DSC/2010/*',
    '/media/chrise/work/audio/dsc/DSC/2011/*',
    '/media/chrise/work/audio/dsc/DSC/2012/*',
    '/media/chrise/work/audio/dsc/DSC/2013/*',
  ]

  loopCount = 60

  for filedir in dir_list:

    pathElements = re.split(r"\x2f", filedir)
    pathYear = pathElements[7]

    srt_path = SRT_DIR
    srt_path = re.sub(r"\x7byear\x7d", pathYear, str(srt_path), flags=re.IGNORECASE)

    mp3files = listMP3files(filedir)
    for filename in mp3files:
      if filename != None:
        if re.search(r"DSC\x2d(\d{4})\x2d(\d{2})\x2d(\d{2}).*\x2emp3$", str(filename), flags=re.IGNORECASE):
        #if re.search(r"\x2emp3$", str(filename), flags=re.IGNORECASE):
          stripped_filename = extractFilename(filename)
          srt_fullpath = f"{srt_path}{stripped_filename}.srt"

          if (
            os.path.isfile(srt_fullpath) == False
            and
            os.path.exists(srt_fullpath) == False
          ):
            cmd = " ".join(CMD_WHISPER)
            cmd = re.sub(r"\x7bsrt\x5fdir\x7d", srt_path, str(cmd), flags=re.IGNORECASE)
            cmd = re.sub(r"\x7bfullpath\x5fmp3\x7d", filename, str(cmd), flags=re.IGNORECASE)
            print(f"Loop: {loopCount}")
            print(cmd)
            os.system(cmd)
            loopCount -= 1

            if loopCount <= 0:
              break

        if re.search(r"DSC\x2d(\d{4})\x2d(\d{2})\x2d(\d{2}).*\x2e(m4v|mp4|mov)$", str(filename), flags=re.IGNORECASE):
        #if re.search(r"\x2emp3$", str(filename), flags=re.IGNORECASE):
          stripped_filename = extractFilename(filename)
          srt_fullpath = f"{srt_path}{stripped_filename}.srt"

          if (
            os.path.isfile(srt_fullpath) == False
            and
            os.path.exists(srt_fullpath) == False
          ):
            cmd = " ".join(CMD_WHISPER)
            cmd = re.sub(r"\x7bsrt\x5fdir\x7d", srt_path, str(cmd), flags=re.IGNORECASE)
            cmd = re.sub(r"\x7bfullpath\x5fmp3\x7d", filename, str(cmd), flags=re.IGNORECASE)
            print(f"Loop: {loopCount}")
            print(cmd)
            os.system(cmd)
            loopCount -= 1

            if loopCount <= 0:
              break


    if loopCount <= 0:
      break


if __name__ == '__main__':
  main()
