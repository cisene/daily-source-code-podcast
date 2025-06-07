#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import yaml

from lxml import etree

from datetime import datetime

from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3  
import mutagen.id3  
from mutagen.id3 import ID3, TIT2, TIT3, TALB, TPE1, TRCK, TYER
from PIL import Image
import glob  
from io import BytesIO

def writeBinary(path, contents):
  if os.path.isfile(path) == False:
    with open(path, 'wb') as img:
     img.write(contents)


def mimetypeToExtension(mimetype):
  result = None
  if re.search(r"^image\x2fjpeg$", str(mimetype), flags=re.IGNORECASE):
    result = "jpg"

  if re.search(r"^image\x2fpng$", str(mimetype), flags=re.IGNORECASE):
    result = "png"


  return result


def makeImgPath(path, instance):
  # /media/chrise/work/audio/dsc/DSC/2004/DSC-2004-12-31.mp3
  path = re.sub(r"audio\x2fdsc\x2fdsc\x2f", "repos/github/cisene/daily-source-code-podcast/img/", str(path), flags=re.IGNORECASE)
  #print(path)
  path = re.sub(r"\x2e(mp3|m4a)$", "", str(path), flags=re.IGNORECASE)
  #print(path)
  if instance != None:
    path = f"{path}-{instance:02}"
  else:
    pass

  return path




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


  for dir in dir_list:
    for filename in sorted(glob.glob(dir, recursive = True)):
      if filename != None:
        if re.search(r"\x2emp3$", str(filename), flags=re.IGNORECASE):
          print(filename)

          mp3file = MP3(filename, ID3=EasyID3)
          track = MP3(filename)
          tags = ID3(filename)
          apic_length = len(track.tags.getall('APIC'))
          apic_instance = 1
          if apic_length >= 1:
            for apic in track.tags.getall('APIC'):
              pict = apic.data
              mime = apic.mime
              im = Image.open(BytesIO(pict))
              picPath = makeImgPath(filename,apic_instance)
              picExt = mimetypeToExtension(mime)
              if picExt == None:
                print(f"Mime was not recognized: '{mime}'")
                exit(0)

              picPathFinal = f"{picPath}.{picExt}"
              if os.path.isfile(picPathFinal) == False:
                print(picPathFinal)
                writeBinary(picPathFinal, pict)

              apic_instance += 1




if __name__ == '__main__':
  main()
