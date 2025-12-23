#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re

import glob
import feedparser

import yaml
import time

#from datetime import datetime
from datetime import datetime, timezone

from io import StringIO
from html.parser import HTMLParser

from bs4 import BeautifulSoup

RSS_DIR = '../rss/*'

EPISODE_DIR = '../yaml/epsodes/'
EPISODE_EXTRACT_DIR = '../rss/episodes/'
EPISODE_LOOKUP = '../yaml/episode-lookup.yaml'


class EpisodeData:
  episode = None
  title = None
  link = None
  pubDate = None
  category = None
  description = None
  author = None
  language = None
  keywords = None
  image = {
    'href': None,
  }
  comments = None
  guid = {
    'isPermaLink' : False,
    'link': None
  }

  enclosure = {
    'url': None,
    'length': None,
    'type': None,
  }

  dc = {
    'author': None,
  }

  content = {
    'encoded': None,
  }

  itunes = {
    'author': None,
    'title': None,
    'subtitle': None,
    'summary': None,
    'explicit': None,
    'keywords': None,
    'duration': None,
    'season': None,
    'episode': None,
    'image': {
      'href': None
    }
  }

  podcast = {
    'episode': None,
    'season': None,
    'title': None,
    'subtitle': None,
    'summary': None,
    'explicit': None,
    'description': None,
    'pubDate': None,
    'license': None,
    'guid': None,
    'keywords': None,

    'location': {
      'geo': None,
      'osm': None,
      'name': None,
    },

    'person': [
      {
        'person': None,
        'href': None,
        'img': None,
        'group': None,
        'role': None,
      }
    ],

    'images': {
      'href': None,
    },

    'chapters': [
      {
        'url': None,
        'type': None,
      }
    ],

    'transcript': [
      {
      'url': None,
      'type': None,
      }
    ],

    'socialInteract': [
      {
        'uri': None,
        'protocol': 'disabled',
        'accountId': None,
        'accountUrl': None,
      }
    ],

    'alternateEnclosure': [
      {
        'type': None,
        'length': None,
        'bitrate': 64000,
        'default': True,
        'title': 'Daily Source Code',
        'source': {
          'uri': None
        }
      }
    ]
  }

  fileinfo = {
    'filename': None,
    'size': None,
  }

  def __init__(self):
    self.title = None

  def __new__(cls):
    return super().__new__(cls)

  def dump(self):
    for attr in dir(self):
      if hasattr( self, attr ):
        print( "obj.%s = %s" % (attr, getattr(self, attr)))

  def toObj(self):
    result = {
      'episode': self.episode,
      'title': self.title,
      'link':  self.link,
      'pubDate': self.pubDate,
      'category': self.category,
      'description': self.description,
      'author': self.author,
      'language': self.language,
      'comments': self.comments,
      'guid': self.guid,
      'dc': self.dc,
      'content': self.content,
      'enclosure': self.enclosure,
      'itunes': self.itunes,
      'podcast': self.podcast,
      'fileinfo': self.fileinfo,
    }

    return result


def writeYAML(filepath, contents):
  s = yaml.safe_dump(
    contents,
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
  contents = None
  data = None
  if os.path.isfile(filepath):
    fp = None

    try:
      fp = open(filepath)
      contents = fp.read()
      fp.close()

    finally:
      pass

  if contents != None:
    data = yaml.safe_load(contents)

  return data

def parseInteger(data):
  if data == None:
    return 0

  if data == "":
    return 0

  value = 0
  data = re.sub(r"[^\d]", "", str(data), flags=re.IGNORECASE)

  if data == "":
    return 0

  try:
    value = int(data, base=10)
  finally:
    pass

  return value



def listRSSfiles(filepath):
  result = []

  for filename in sorted(glob.glob(filepath, recursive = True)):
    if filename != None:
      if re.search(r"\x2exml$", str(filename), flags=re.IGNORECASE):
        if filename not in result:
          result.append(filename)

  return result


def cleanupHTML(data):

  # replace all LF
  data = re.sub(r"\r", "", str(data), flags=re.IGNORECASE)
  data = re.sub(r"\r", "", str(data), flags=re.IGNORECASE)

  data = re.sub(r"\t", "    ", str(data), flags=re.IGNORECASE)

  # remove strange character
  data = re.sub(r"\xa0", "", str(data), flags=re.IGNORECASE)

  # replace double single quotes
  data = re.sub(r"\x27\x27", "'", str(data), flags=re.IGNORECASE)

  # replace all br elements
  data = re.sub(r"\x3cbr((\s)?\x2f)?\x3e", "\n", str(data), flags=re.IGNORECASE)

  # replace empty alt attributes
  data = re.sub(r"\salt\x3d\x22\x22", " alt=\"[Image]\"", str(data), flags=re.IGNORECASE)

  # remove size attribute from everything
  data = re.sub(r"\ssize\x3d\x22.+?\x22", "", str(data), flags=re.IGNORECASE)

  # remove face attribute from everything
  data = re.sub(r"\sface\x3d\x22.+?\x22", "", str(data), flags=re.IGNORECASE)

  # remove style attributes from everything
  data = re.sub(r"\sstyle\x3d\x22.+?\x22", "", str(data), flags=re.IGNORECASE)

  # remove font elements
  data = re.sub(r"\x3c(\x2f)?font\x3e", "", str(data), flags=re.IGNORECASE)


  data = re.sub(r"\n", "<br>", str(data), flags=re.IGNORECASE)

  data = re.sub(r"^\s{1,}", "", str(data), flags=re.IGNORECASE)
  data = re.sub(r"\s{1,}$", "", str(data), flags=re.IGNORECASE)
  data = re.sub(r"\s{2,}", " ", str(data), flags=re.IGNORECASE)

  # Remove "air" between elements
  data = re.sub(r"\x3e\s{1,}\x3c", "><", str(data), flags=re.IGNORECASE)

  # Remove "air" after an element an a word
  data = re.sub(r"\x3e\s{1,}\b", ">", str(data), flags=re.IGNORECASE)

  # Remove "air" before and element after a word
  data = re.sub(r"\b\s{1,}\x3c", "<", str(data), flags=re.IGNORECASE)


  return data

def parseDescription(description):
  description = re.sub(r"\t", "  ", str(description), flags=re.IGNORECASE)
  description = re.sub(r"(\r\n|\r|\n)", "\n", str(description), flags=re.IGNORECASE)
  description = re.sub(r"\x3cbr(\s)?(\x2f)?(\s)?\x3f", "\n", str(description), flags=re.IGNORECASE)

  soup = BeautifulSoup(description, features="lxml")
  description = soup.get_text()

  description = re.sub(r"^\s{1,}", "", str(description), flags=re.IGNORECASE)
  description = re.sub(r"\s{1,}$", "", str(description), flags=re.IGNORECASE)
  description = re.sub(r"\s{2,}", " ", str(description), flags=re.IGNORECASE)  

  return description


def parseSummary(summary):

  summary = re.sub(r"\xa0", "", str(summary), flags=re.IGNORECASE)

  return summary

def parseGUID(link):
  pass

def parseLinks(links):
  result = None
  for link in links:

    if "href" in link and "rel" in link:
      link_href = link['href']
      link_rel = link['rel']


      if link_rel == "alternate":

        # http://homepage.mac.com/adamcurry/gems/to-adam-from-dawn.mp3
        if link_href == "http://homepage.mac.com/adamcurry/gems/to-adam-from-dawn.mp3":
          result = {}
          result['episode'] = "48.5"
          result['isDSC'] = True

        # http://homepage.mac.com/adamcurry/gems/ipodder.mp4
        if link_href == "http://homepage.mac.com/adamcurry/gems/ipodder.mp4":
          result = {}
          result['episode'] = "48.4"
          result['isDSC'] = True


        # http://www.blognewsnetwork.com/members/0000001/opml/DSC-2004-11-17.opml
        if re.search(r"^http(s)?\x3a.*\x2fdsc\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})\x2eopml$", str(link_href), flags=re.IGNORECASE):
          date_prep = re.sub(r"^http(s)?\x3a.*\x2fdsc\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})\x2eopml$", "\\2-\\3-\\4", str(link_href), flags=re.IGNORECASE)
          result = {}
          result['date'] = datetime.strptime(date_prep, '%Y-%m-%d').strftime('%Y-%m-%d')
          result['isDSC'] = True

        # http://www.mevio.com/episode/140614/dsc-819-2009-01-23
        if re.search(r"^http(s)?\x3a.*\x2fdsc\x2d(\d{3})\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})$", str(link_href), flags=re.IGNORECASE):
          date_prep = re.sub(r"^http(s)?\x3a.*\x2fdsc\x2d(\d{3})\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})$", "\\3-\\4-\\5|\\2", str(link_href), flags=re.IGNORECASE)
          elem = re.split(r"\x7c", str(date_prep))
          result = {}
          result['date'] = datetime.strptime(elem[0], '%Y-%m-%d').strftime('%Y-%m-%d')
          result['episode'] = elem[1]
          result['isDSC'] = True

        # http://radio.weblogs.com/0001014/categories/dailySourceCode/2004/08/27.html#a6456
        if re.search(r"^http(s)?\x3a.*\x2fdailySourceCode\x2f(\d{4})\x2f(\d{2})\x2f(\d{2})\x2ehtml\x23[0-9a-f]{1,}$", str(link_href), flags=re.IGNORECASE):
          date_prep = re.sub(r"^http(s)?\x3a.*\x2fdailySourceCode\x2f(\d{4})\x2f(\d{2})\x2f(\d{2})\x2ehtml\x23[0-9a-f]{1,}$", "\\2-\\3-\\4", str(link_href), flags=re.IGNORECASE)
          result = {}
          result['date'] = datetime.strptime(date_prep, '%Y-%m-%d').strftime('%Y-%m-%d')
          result['isDSC'] = True

        # http://mp3.dailysourcecode.podshow.com/DSC-2005-06-16.mp3
        if re.search(r"^http(s)?\x3a.*\x2fdsc\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})\x2emp3$", str(link_href), flags=re.IGNORECASE):
          date_prep = re.sub(r"^http(s)?\x3a.*\x2fdsc\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})\x2emp3$", "\\2-\\3-\\4", str(link_href), flags=re.IGNORECASE)
          result = {}
          result['date'] = datetime.strptime(date_prep, '%Y-%m-%d').strftime('%Y-%m-%d')
          result['isDSC'] = True

        # http://www.blognewsnetwork.com/members/0000001/2004/08/21.html#a6385
        if re.search(r"^http(s)?\x3a\x2f\x2fwww\x2eblognewsnetwork\x2ecom\x2fmembers\x2f.+?\x2f(\d{4})\x2f(\d{2})\x2f(\d{2})\x2ehtml.+?$", str(link_href), flags=re.IGNORECASE):
          date_prep = re.sub(r"^http(s)?\x3a\x2f\x2fwww\x2eblognewsnetwork\x2ecom\x2fmembers\x2f.+?\x2f(\d{4})\x2f(\d{2})\x2f(\d{2})\x2ehtml.+?$", "\\2-\\3-\\4", str(link_href), flags=re.IGNORECASE)
          result = {}
          result['date'] = datetime.strptime(date_prep, '%Y-%m-%d').strftime('%Y-%m-%d')
          result['isDSC'] = True

      if link_rel == "enclosure":

        # http://adam.opml.org/DSC20041117.mp3
        if re.search(r"^http(s)?\x3a.*\x2fdsc(\d{4})(\d{2})(\d{2})\x2emp3$", str(link_href), flags=re.IGNORECASE):
          date_prep = re.sub(r"^http(s)?\x3a.*\x2fdsc(\d{4})(\d{2})(\d{2})\x2emp3$", "\\2-\\3-\\4", str(link_href), flags=re.IGNORECASE)
          result = {}
          result['date'] = datetime.strptime(date_prep, '%Y-%m-%d').strftime('%Y-%m-%d')
          result['isDSC'] = True

        # http://cloud2.urj.nl/gems/dailySourceCode08272004.mp3
        if re.search(r"^http(s)?\x3a.*\x2f(dailysourcecode)(\d{2})(\d{2})(\d{4})\x2emp3$", str(link_href), flags=re.IGNORECASE):
          link_href = re.sub(r"^http(s)\x3a\x2f\x2f.+?\x2f", "", str(link_href), flags=re.IGNORECASE)
          link_href = re.sub(r".*\x2f", "", str(link_href), flags=re.IGNORECASE)
          date_prep = re.sub(r"dailysourcecode(\d{2})(\d{2})(\d{4})\x2emp3$", "\\3-\\1-\\2", str(link_href), flags=re.IGNORECASE)
          result = {}
          result['date'] = datetime.strptime(date_prep, '%Y-%m-%d').strftime('%Y-%m-%d')
          result['isDSC'] = True

        # http://cloud2.urj.nl/gems/dailySourceCode200408212004.mp3 - typo
        if re.search(r"^http(s)?\x3a.*\x2f(dailySourceCode)(\d{4})(\d{2})(\d{2})(\d{4})\x2emp3$", str(link_href), flags=re.IGNORECASE):
          date_prep = re.sub(r"^http(s)?\x3a.*\x2f(dailySourceCode)(\d{4})(\d{2})(\d{2})(\d{4})\x2emp3$", "\\4-\\2-\\3", str(link_href), flags=re.IGNORECASE)
          result = {}
          result['date'] = datetime.strptime(date_prep, '%Y-%m-%d').strftime('%Y-%m-%d')
          result['isDSC'] = True

        # http://m.podshow.com/media/21/episodes/142388/dailysourcecode-142388-02-04-2009.mp3
        if re.search(r"^http(s)?\x3a.*\x2f(dailysourcecode)\x2d\d{4,6}\x2d(\d{2})\x2d(\d{2})\x2d(\d{4})\x2emp3$", str(link_href), flags=re.IGNORECASE):
          link_href = re.sub(r"^http(s)?\x3a\x2f\x2f.+?\x2f", "", str(link_href), flags=re.IGNORECASE)
          link_href = re.sub(r".*\x2f", "", str(link_href), flags=re.IGNORECASE)
          link_href = re.sub(r".*\x2f", "", str(link_href), flags=re.IGNORECASE)
          link_href = re.sub(r"\x2emp3$", "", str(link_href), flags=re.IGNORECASE)
          date_prep = re.sub(r"^dailysourcecode\x2d\d{4,6}\x2d(\d{2})\x2d(\d{2})\x2d(\d{4})$", "\\3-\\1-\\2", str(link_href), flags=re.IGNORECASE)
          result = {}
          result['date'] = datetime.strptime(date_prep, '%Y-%m-%d').strftime('%Y-%m-%d')
          result['isDSC'] = True
          pass



      #if result == None:
      #  print(f"Has link '{link_href}' and rel '{link_rel}'")

    if result != None:
      if "isDSC" in result:
        break

      if "date" in result:
        break
    #else:
    #  print(f"Has link '{link_href}' and rel '{link_rel}'")


  if result == None:
    print(links)
    #exit(0)

  return result


def parsePubDate(pubDate):
  result = {}
  publishDate = None
  
  # If value is null, bail out early
  if pubDate == None:
    return None

  #print(f"pubDate: '{pubDate}'")

  # Mon, 06 Dec 2004 16:47:30 GMT
  if re.search(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\x2c\s(\d{1,2})\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(\d{4})\s(\d{2})\x3a(\d{2})\x3a(\d{2})\s(GMT)$", str(pubDate), flags=re.IGNORECASE):
    pubDate = re.sub(r"\sGMT", " +0000", str(pubDate), flags=re.IGNORECASE)
    try:
      publishDate = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %z').astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
    except ValueError:
      pass
    finally:
      pass

  # Fri, 27 Aug 2004 14:03:26 GMT
  # datetime.strptime(str, "%Y-%m-%dT%H:%M:%S%z")
  #try:
  #  publishDate = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %z').strftime('%Y-%m-%dT%H:%M:%S')
  #except ValueError:
  #  pass
  #finally:
  #  pass

  # Fri, 19 Oct 2007 09:01:22 -0700
  try:
    publishDate = datetime.strptime(pubDate, '%a, %d %b %Y %H:%M:%S %z').astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+0000')
  except ValueError:
    pass
  finally:
    pass

  if publishDate:

    result['pubDate'] = str(publishDate)
    result['episodeDate'] = datetime.strptime(publishDate, '%Y-%m-%dT%H:%M:%S%z').strftime('%Y-%m-%d')
    result['pubDateFormatted'] = datetime.strptime(publishDate, '%Y-%m-%dT%H:%M:%S%z').strftime('%c %z')

    # Daily Source Code for Sunday August 22nd 2004
    result['titleDate'] = datetime.strptime(publishDate, '%Y-%m-%dT%H:%M:%S%z').strftime('%A %B %d %Y')
  else:
    print(f"Format not recognized: '{pubDate}'")


  if "pubDate" not in result:
    result = None
    print(f"pubDate: '{pubDate}'")

  #print(result)

  return result


def parseTitle(title):
  result = {}

  title = re.sub(r"\x20(\d{1,2})st\x20", " \\1 ", str(title), flags=re.IGNORECASE)
  title = re.sub(r"\x20(\d{1,2})d\x20", " \\1 ", str(title), flags=re.IGNORECASE)
  title = re.sub(r"\x20(\d{1,2})rd\x20", " \\1 ", str(title), flags=re.IGNORECASE)
  title = re.sub(r"\x20(\d{1,2})nd\x20", " \\1 ", str(title), flags=re.IGNORECASE)
  title = re.sub(r"\x20(\d{1,2})th\x20", " \\1 ", str(title), flags=re.IGNORECASE)

  title = re.sub(r"\x20(Mon|Tue|Tues|Wed|Thu|Thurs|Fri|Sat|Sun)\x2e\x20", " ", str(title), flags=re.IGNORECASE)
  title = re.sub(r"\x20(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\x20", " ", str(title), flags=re.IGNORECASE)

  title = re.sub(r"\x20(Monday|Tuesday|Tursday|Wednesday|Wenesday|Wedenesday|Thursday|Thursdy|Thurssday|Friday|Saturday|Sunday)\x20", " ", str(title), flags=re.IGNORECASE)

  title = re.sub(r"\x20Feb\x20", " February ", str(title), flags=re.IGNORECASE)
  title = re.sub(r"\x20Aug\x20", " August ", str(title), flags=re.IGNORECASE)
  
  # Typo
  title = re.sub(r"\x20Janury\x20", " January ", str(title), flags=re.IGNORECASE)

  # Typo
  title = re.sub(r"\x20Dource\x20", " Source ", str(title), flags=re.IGNORECASE)


  #21:14:27 CEST
  title = re.sub(r"\x20\d{2}\x3a\d{2}\x3a\d{2}\x20", " ", str(title), flags=re.IGNORECASE)
  title = re.sub(r"\x20CEST\x20", " ", str(title), flags=re.IGNORECASE)

  title = re.sub(r"^Repost\x20of\x20", "", str(title), flags=re.IGNORECASE)
  title = re.sub(r"\x20\x28repost\x29\x20", "", str(title), flags=re.IGNORECASE)


  # Daily Source Code
  if re.search(r"^(daily\ssource\scode)$", str(title), flags=re.IGNORECASE):
    # Won't get any other data here...
    result['title'] = "Daily Source Code"
    result['isDSC'] = True

  # daily source code august 27 2004
  if re.search(r"^daily\ssource\scode\s(january|february|march|april|may|june|july|august|september|october|november|december)\s(\d{1,})\s(\d{4})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^daily\ssource\scode\s(january|february|march|april|may|june|july|august|september|october|november|december)\s(\d{1,})\s(\d{4})$", "Daily Source Code \\1 \\2 \\3|\\1 \\2 \\3", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 2:
      result['title'] = str(title_elem[0])
      result['date'] = datetime.strptime(title_elem[1], '%B %d %Y').strftime('%Y-%m-%d')
      result['isDSC'] = True

  # source code august 27 2004
  if re.search(r"^source\scode\s(january|february|march|april|may|june|july|august|september|october|november|december)\s(\d{1,})\s(\d{4})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^source\scode\s(january|february|march|april|may|june|july|august|september|october|november|december)\s(\d{1,})\s(\d{4})$", "Daily Source Code \\1 \\2 \\3|\\1 \\2 \\3", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 2:
      result['title'] = str(title_elem[0])
      result['date'] = datetime.strptime(title_elem[1], '%B %d %Y').strftime('%Y-%m-%d')
      result['isDSC'] = True

  # source code august 23 2004 20:09
  if re.search(r"^source\scode\s(january|february|march|april|may|june|july|august|september|october|november|december)\s(\d{1,})\s(\d{4})\s\d{2}\x3a\d{2}$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^source\scode\s(january|february|march|april|may|june|july|august|september|october|november|december)\s(\d{1,})\s(\d{4})\s\d{2}\x3a\d{2}$", "Daily Source Code \\1 \\2 \\3|\\1 \\2 \\3", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 2:
      result['title'] = str(title_elem[0])
      result['date'] = datetime.strptime(title_elem[1], '%B %d %Y').strftime('%Y-%m-%d')
      result['isDSC'] = True

  # DSC-737-2008-03-21
  # DSC-592-2007-05-01
  if re.search(r"^DSC\x2d(\d{1,})\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^DSC\x2d(\d{1,})\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})$", "Daily Source Code \\1|\\1|\\2-\\3-\\4", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 3:
      #result['title'] = str(title_elem[0])
      result['episode'] = str(title_elem[1])
      result['date'] = datetime.strptime(title_elem[2], '%Y-%m-%d').strftime('%Y-%m-%d')
      result['title'] = f"Daily Source Code for {datetime.strptime(result['date'], '%Y-%m-%d').strftime('%A %B %d %Y')}"
      result['isDSC'] = True

  # DSC-808-11-27-2008
  if re.search(r"^DSC\x2d(\d{3})\x2d(\d{2})\x2d(\d{2})\x2d(\d{4})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^DSC\x2d(\d{3})\x2d(\d{2})\x2d(\d{2})\x2d(\d{4})$", "Daily Source Code|\\4-\\2-\\3|\\1", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 3:
      result['episode'] = str(title_elem[2])
      result['date'] = datetime.strptime(title_elem[1], '%Y-%m-%d').strftime('%Y-%m-%d')
      result['title'] = f"Daily Source Code for {datetime.strptime(result['date'], '%Y-%m-%d').strftime('%A %B %d %Y')}"
      result['isDSC'] = True

  # daily source code september 22 20004 (special case)
  if re.search(r"^daily\ssource\scode\s(january|february|march|april|may|june|july|august|september|october|november|december)\s(\d{1,})\s(\d{5})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^daily\ssource\scode\s(january|february|march|april|may|june|july|august|september|october|november|december)\s(\d{1,})\s(\d{5})$", "Daily Source Code \\1 \\2 \\3|\\1 \\2 \\3", str(title), flags=re.IGNORECASE)
    title_prep = re.sub(r"0{3}", "00", str(title_prep), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 2:
      result['title'] = str(title_elem[0])
      result['date'] = datetime.strptime(title_elem[1], '%B %d %Y').strftime('%Y-%m-%d')
      result['isDSC'] = True

  # Daily Source Code for January 5th 2005
  # daily souce code september 16 2004
  # Daily Source Code for January 6 2005
  if re.search(r"^(daily\ssource\scode)\sfor\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})([strdh]{1,})?\s(\d{4})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^(daily\ssource\scode)\sfor\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})([strdh]{1,})?\s(\d{4})$", "Daily Source Code for \\2 \\3 \\4|\\2 \\3 \\5", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 2:
      result['title'] = str(title_elem[0])
      result['date'] = datetime.strptime(title_elem[1], '%B %d %Y').strftime('%Y-%m-%d')
      result['isDSC'] = True

  # DSC-2004-11-17-OPML
  if re.search(r"^(dsc)\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})\x2d(opml)$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^(dsc)\x2d(\d{4})\x2d(\d{2})\x2d(\d{2})\x2d(opml)$", "Daily Source Code|\\2-\\3-\\4", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 2:
      result['date'] = datetime.strptime(title_elem[1], '%Y-%m-%d').strftime('%Y-%m-%d')
      result['title'] = f"Daily Source Code for {datetime.strptime(result['date'], '%Y-%m-%d').strftime('%A %B %d %Y')}"
      result['isDSC'] = True

  if re.search(r"^\x23(\d{3})\s(Daily\sSource\sCode)\sfor\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})\s(\d{4})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^\x23(\d{3})\s(Daily\sSource\sCode)\sfor\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})\s(\d{4})$", "Daily Source Code for \\3 \\4 \\5|\\3 \\4 \\5|\\1", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 3:
      result['title'] = title_elem[0]
      result['date'] = datetime.strptime(title_elem[1], '%B %d %Y').strftime('%Y-%m-%d')
      result['episode'] = title_elem[2]
      result['isDSC'] = True

  # Daily Source Code for August 26 2005 #229
  if re.search(r"^Daily\sSource\sCode\sfor\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})\s(\d{4})\s\x23(\d{3})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^Daily\sSource\sCode\sfor\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})\s(\d{4})\s\x23(\d{3})$", "Daily Source Code for \\1 \\2 \\3|\\1 \\2 \\3|\\4", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 3:
      result['title'] = title_elem[0]
      result['date'] = datetime.strptime(title_elem[1], '%B %d %Y').strftime('%Y-%m-%d')
      result['episode'] = title_elem[2]
      result['isDSC'] = True

  if re.search(r"^Daily\sSource\sCode\sfor\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})\s(\d{4})$", str(title), flags=re.IGNORECASE):
    title_prep = re.sub(r"^Daily\sSource\sCode\sfor\s(January|February|March|April|May|June|July|August|September|October|November|December)\s(\d{1,2})\s(\d{4})$", "Daily Source Code for \\1 \\2 \\3|\\1 \\2 \\3", str(title), flags=re.IGNORECASE)
    title_elem = re.split(r"\x7c", title_prep, flags=re.IGNORECASE)
    if len(title_elem) == 2:
      result['title'] = title_elem[0]
      result['date'] = datetime.strptime(title_elem[1], '%B %d %Y').strftime('%Y-%m-%d')
      result['isDSC'] = True



  # Special case
  if re.search(r"DSC\x2dSpecial\sAnnouncement$", str(title), flags=re.IGNORECASE):
    result['title'] = title
    result['isDSC'] = True


  # NA-xxx-
  if re.search(r"^NA\x2d\d{3}\x2d\d{4}\x2d\d{2}\x2d\d{2}$", str(title), flags=re.IGNORECASE):
    result['title'] = title
    result['isDSC'] = False


  # Fallthrough - nothing matched
  #if "title" not in result:
  #  result['title'] = title
  # result['isDSC'] = False

  #print(result)
  if len(result) == 0:
    result = None

  return result


def padEpisodes():
  global lookup

  for ep in range(1, 868):
    ep_key = f"{ep:03}"
    if str(ep_key) not in lookup['episodes']:
      lookup['episodes'][str(ep_key)] = None
    else:
      ep_date = lookup['episodes'][ep_key]
      if ep_date != None:
        if ep_date not in lookup['dates']:
          lookup['dates'][ep_date] = str(ep_key)

  for dt in lookup['dates']:
    if dt != None:
      episode = lookup['dates'][dt]
      if episode != None:
        if lookup['episodes'][str(episode)] == None:
          lookup['episodes'][str(episode)] = str(dt)

  return



def processFiles(filelist):
  global lookup
  for file in filelist:
    print(file)


    feed = feedparser.parse(file)
    
    skip_titles = [
      "trade secrets september 22 2004",
      "no source 2day",
      "DSC Commercial",
    ]

    for entry in feed.entries:
      episodeId = None
      episodeDate = None

      episodeParse = False

      for e in entry.keys():
        known = [
          'title',
          'title_detail',
          'authors',
          'author',
          'author_detail',
          'links',
          'link',
          'summary',
          'summary_detail',
          'subtitle',
          'subtitle_detail',
          'content',
          'published',
          'published_parsed',
          'tags',
          'itunes_explicit',
          'id',
          'guidislink',
          'image',
          'comments',
          'wfw_commentrss',
        ]
        if e not in known:
          print(e)
          #exit(0)


      if entry:
        title = None
        pubDate = None

        episodeId = None

        dateInfo = None
        titleInfo = None
        linksInfo = None

        item = EpisodeData()

        if "links" in entry:
          if entry.links != None:
            linksInfo = parseLinks(entry.links)

            if linksInfo != None:
              if "isDSC" in linksInfo:
                if linksInfo['isDSC'] == True:
                  pass

                if "episode" in linksInfo:
                  if linksInfo['episode'] != None:
                    episodeId = linksInfo['episode']
                else:
                  if linksInfo['date'] != None:
                    if str(linksInfo['date']) in lookup['dates']:
                      episodeId = lookup['dates'][str(linksInfo['date'])]
                      print(f"date '{linksInfo['date']}' -> {episodeId}")

                      # Non-existing date, add it (for investigation)
                      if episodeId == None and linksInfo['date'] != None:
                        lookup['dates'][str(linksInfo['date'])] = None

        if "published" in entry:
          if entry.published != None:
            dateInfo = parsePubDate(entry.published)

        if "title" in entry:
          if entry.title != None:
            titleInfo = parseTitle(entry.title)

        if linksInfo == None:
          #print(entry)
          #exit(0)
          pass

        episodeParse = False
        if "links" in entry:
          if entry.links:
            if entry.links != None:
              for link in entry.links:

                if link['rel'] == 'enclosure':
                  mime_types = [
                    'audio/mp3',
                    'audio/mp4',
                    'audio/mpeg',
                    'audio/x-mpeg',
                    'video/mp4',
                    'video/quicktime',
                    'video/x-m4v',
                  ]

                  mime_types_wrong = [
                    '',
                    'text/html',
                    'text/html; charset=utf-8',
                    'text/plain',
                    'text/plain; charset=utf-8',
                  ]

                  if link['type'] in mime_types_wrong:
                    if re.search(r"\x2e(mp4|m4v)$", str(link['href']), flags=re.IGNORECASE):
                      link['type'] = 'video/mp4'

                    if re.search(r"\x2e(mov)$", str(link['href']), flags=re.IGNORECASE):
                      link['type'] = 'video/quicktime'

                    if re.search(r"\x2e(mp3|m4a|m4b)$", str(link['href']), flags=re.IGNORECASE):
                      link['type'] = 'audio/mpeg'

                  if link['type'] in mime_types:
                    episodeParse = True

                    item.enclosure['url'] = link['href']
                    item.enclosure['type'] = link['type']
                    item.enclosure['length'] = parseInteger(link['length'])
                    
                    altEnclosure = {
                      'type': link['type'],
                      'length': link['length'],
                      'bitrate': None,
                      'default': False,
                      'title': entry.title,
                      'source': {
                        'uri': link['href']
                       }
                    }

                    item.podcast['alternateEnclosure'][0] = altEnclosure

        if episodeParse == False:
          continue

        if dateInfo == None:
          if "published" in entry:
            print(f"published: '{entry.published}'")
          
          if "published_parsed" in entry:
            print(f"published_parsed: '{entr.published_parsed}")

          print("-- dateInfo --")
          print(entry)
          #exit(0)
          pass

        if titleInfo == None:
          print(f"title: '{entry.title}'")
          print(titleInfo)
          print("-- titleInfo --")
          if dateInfo != None:
            print(dateInfo)
            synthetic_title = f"Daily Source Code for {dateInfo['titleDate']}"
            print(synthetic_title)
            if dateInfo['episodeDate'] in lookup['dates']:
              episodeId = lookup['dates'][dateInfo['episodeDate']]
            entry.title = synthetic_title
            titleInfo = {
              'title': synthetic_title,
              'isDSC': True,
              'date': dateInfo['episodeDate'],
              'episode': episodeId
            }
          #exit(0)


        if titleInfo != None:

          if "isDSC" in titleInfo:
            if titleInfo['isDSC'] == True:

              if "episode" not in titleInfo:
                if "date" in titleInfo:
                  if titleInfo['date'] in lookup['dates']:
                    episodeId = lookup['dates'][titleInfo['date']]
                  else:
                    print(f"'{titleInfo['date']}' is not in lookup")
              else:
                episodeId = titleInfo['episode']
            else:
              print("Not a DSC episode ..")
              #continue

          if "title" in titleInfo:
            if titleInfo['title'] != None:
              item.title = titleInfo['title']
              item.itunes['title'] = titleInfo['title']
              item.podcast['title'] = titleInfo['title']

              item.category = "podcast"
              item.language = "en-us"



        else:
          print("titleInfo was null")


          
          if "subtitle" in entry:
            if entry.title == None and entry.subtitle != None:
              print(f"title: '{entry.title}'")
              print(f"subtitle: '{entry.subtitle}'")




        if episodeId != None:
          item.episode = episodeId
          item.itunes['episode'] = episodeId
          item.podcast['episode'] = episodeId

        if "image" in entry:
          if entry.image:
            if entry.image != None:
              if entry.image.href != None:
                item.image['href'] = entry.image.href

                item.itunes['image']['href'] = entry.image.href
                item.podcast['images']['href'] = entry.image.href

        if "subtitle" in entry:
          if entry.subtitle:
            if entry.subtitle != None:
              item.itunes['subtitle'] = entry.subtitle
              item.podcast['subtitle'] = entry.subtitle
        else:
          item.itunes['subtitle'] = None
          item.podcast['subtitle'] = None


        if "published" in entry:
          if entry.published:
            if entry.published != None:
              #dateInfo = parsePubDate(entry.published)
              item.pubDate = dateInfo['pubDateFormatted']
              item.itunes['pubDate'] = dateInfo['pubDateFormatted']
              item.podcast['pubDate'] = dateInfo['pubDateFormatted']

        if "link" in entry:
          if entry.link:
            if entry.link != None:
              item.link = entry.link
              item.guid['link'] = entry.link

        if "guidislink" in entry:
          if entry.guidislink:
            if entry.guidislink != None:
              item.guid['isPermaLink'] = entry.guidislink


        if "language" in entry:
          if entry.language:
            if entry.language != None:
              item.language = entry.language
        else:
          item.language = "en-us"

        if "description" in entry:
          if entry.description:
            if entry.description != None:
              description = parseDescription(entry.description)
              item.description = cleanupHTML(description)
        else:
          item.description = None


        if "summary" in entry:
          if entry.summary:
            if entry.summary != None:
              item.itunes['summary'] = cleanupHTML(parseSummary(entry.summary))
              item.podcast['summary'] = cleanupHTML(parseSummary(entry.summary))
        else:
          item.itunes['summary'] = None
          item.podcast['summary'] = None


        if "author" in entry:
          if entry.author:
            if entry.author != None:
              item.author = entry.author
              item.itunes['author'] = entry.author
              item.dc['author'] = entry.author

              if entry.author == "Adam Curry":
                person = {
                  'person': "Adam Curry",
                  'href': "http://curry.com/",
                  'img': "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Adam_Curry_2016.jpg/440px-Adam_Curry_2016.jpg",
                  'group': "cast",
                  'role': "host",
                }
                item.podcast['person'][0] = person
        else:
          item.author = "Adam Curry"
          item.itunes['author'] = "Adam Curry"
          item.dc['author'] = "Adam Curry"

          person = {
            'person': "Adam Curry",
            'href': "http://curry.com/",
            'img': "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/Adam_Curry_2016.jpg/440px-Adam_Curry_2016.jpg",
            'group': "cast",
            'role': "host",
          }
          item.podcast['person'][0] = person


        if "itunes_explicit" in entry:
          if entry.itunes_explicit:
            if entry.itunes_explicit != None:
              item.itunes['explicit'] = entry.itunes_explicit
              item.podcast['explicit'] = entry.itunes_explicit
        else:
          item.itunes['explicit'] = True
          item.podcast['explicit'] = True


        if "tags" in entry:
          if entry.tags:
            if entry.tags != None:
              keywords = []
              keywords.append("adam")
              keywords.append("curry")
              keywords.append("delta")
              keywords.append("sierra")
              keywords.append("charlie")

              for t in entry.tags:
                if "term" in t:
                  if t['term'] != None:
                    if t['scheme'] == "http://www.itunes.com/":
                      if t['term'].lower() not in keywords:
                        keywords.append(t['term'].lower())

              item.itunes['keywords'] = ",".join(keywords)
              item.podcast['keywords'] = item.itunes['keywords']
        else:
          keywords = []
          keywords.append("adam")
          keywords.append("curry")
          keywords.append("delta")
          keywords.append("sierra")
          keywords.append("charlie")

          item.itunes['keywords'] = ",".join(keywords)
          item.podcast['keywords'] = item.itunes['keywords']

        if "content" in entry:
          if entry.content:
            if entry.content != None:
              encoded = None
              for c in entry.content:
                if c['type'] == "text/plain" and c['value'] != None:
                  encoded = c['value']
                  if item.content['encoded'] == None:
                    #item.content['encoded'] = cleanupHTML(encoded)
                    encoded = None
        else:
          item.content['encoded'] = None

        if item.episode != None:
          file_extract_path = f"{EPISODE_EXTRACT_DIR}{item.episode}.yaml"

          writeYAML(file_extract_path, item.toObj())
          print(f"\tWrote {file_extract_path} ..")
          item = None
        else:
          item = None


def main():
  global lookup

  lookup = readYAML(EPISODE_LOOKUP)
  if lookup == None:
    lookup = {}
    lookup['episodes'] = {}
    lookup['dates'] = {}

  padEpisodes()
  writeYAML(EPISODE_LOOKUP, lookup)

  rssFiles = listRSSfiles(RSS_DIR)

  processFiles(rssFiles)

  writeYAML(EPISODE_LOOKUP, lookup)


if __name__ == '__main__':
  main()
