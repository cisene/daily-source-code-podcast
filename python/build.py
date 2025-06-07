#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import yaml

from lxml import etree

from datetime import datetime

import types

import glob

CONFIG_MAIN = '../yaml/daily-source-code.yaml'
ITEMS_PATH = '../yaml/episodes/'

RSS_PATH = '../daily-source-code.rss'

APPLICATION_NAME = 'EpilectricalSquirrel'
APPLICATION_VERSION = '0.1'


def writeRSS(filepath, contents):
  pass

def writeYAML(filepath, contents):
  pass


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



def main():

  # Read main config
  main_config = readYAML(CONFIG_MAIN)
  if main_config == None:
    print("Config in {CONFIG_MAIN} unreadable")
    exit(127)

# xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:podcast="https://github.com/Podcastindex-org/podcast-namespace/blob/main/docs/1.0.md" xmlns:atom="http://www.w3.org/2005/Atom"

  nsmap = { }
  for ns in main_config['feed']['xml']['namespaces']:
    if ns not in nsmap:
      nsmap[ns] = main_config['feed']['xml']['namespaces'][ns]

  # Open RSS
  rss = etree.Element("rss", version = "2.0", nsmap = nsmap)

  # Open Channel
  channel = etree.SubElement(rss, "channel")

  # Iterate Atom
  for at in main_config['channel']['atom']:
    tag_ns = f"{main_config['feed']['xml']['namespaces']['atom']}"
    tag_name = "".join(["{", f"{tag_ns}", "}", f"{at}"])
    tag_attribs = main_config['channel']['atom'][at]

    elem = etree.Element(tag_name, nsmap = nsmap)
    for attr in main_config['channel']['atom'][at]:
      elem.set(attr, main_config['channel']['atom'][at][attr])
      channel.append(elem)

  # Title element
  sube = etree.SubElement(channel, "title")
  sube.text = main_config['channel']['title']

  # Description element
  sube = etree.SubElement(channel, "description")
  sube.text = main_config['channel']['description']

  # Link element
  sube = etree.SubElement(channel, "link")
  sube.text = main_config['channel']['link']

  # Generator element
  sube = etree.SubElement(channel, "generator")
  sube.text = f"{APPLICATION_NAME}/{APPLICATION_VERSION}"

  # pubDate element
  sube = etree.SubElement(channel, "pubDate")
  sube.text = "Fri, 13 Aug 2004 21:36:44 +0000"

  # LastBuildDate element
  sube = etree.SubElement(channel, "lastBuildDate")
  sube.text = "now()"

  # Docs element
  sube = etree.SubElement(channel, "docs")
  sube.text = main_config['channel']['docs']

  # Category element
  sube = etree.SubElement(channel, "category")
  sube.text = main_config['channel']['category']

  # Language element
  sube = etree.SubElement(channel, "language")
  sube.text = main_config['channel']['language']

  # Copyright element
  sube = etree.SubElement(channel, "copyright")
  sube.text = main_config['channel']['copyright']

  # Managing Editor element
  sube = etree.SubElement(channel, "managingEditor")
  sube.text = main_config['channel']['managingEditor']

  # Webmaster element
  sube = etree.SubElement(channel, "webMaster")
  sube.text = main_config['channel']['webMaster']

  # TTL element
  sube = etree.SubElement(channel, "ttl")
  sube.text = str(main_config['channel']['ttl'])

  # Exception, <image> has structure
  image = etree.SubElement(channel, "image")

  # Exception, url subelement
  sube = etree.SubElement(image, "url")
  sube.text = main_config['channel']['image']['url']

  # Exception, link subelement
  sube = etree.SubElement(image, "link")
  sube.text = main_config['channel']['image']['link']

  # Exception, title subelement
  sube = etree.SubElement(image, "title")
  sube.text = main_config['channel']['image']['title']

  # Exception, description subelement
  sube = etree.SubElement(image, "description")
  sube.text = main_config['channel']['image']['description']

  # Exception, width subelement
  sube = etree.SubElement(image, "width")
  sube.text = str(main_config['channel']['image']['width'])

  # Exception, height subelement
  sube = etree.SubElement(image, "height")
  sube.text = str(main_config['channel']['image']['height'])

  # Itunes
  for idx in main_config['channel']['itunes'].keys():

    # Strings
    if isinstance(main_config['channel']['itunes'][idx], str) == True:
      tag_ns = f"{main_config['feed']['xml']['namespaces']['itunes']}"
      tag_name = "".join(["{", f"{tag_ns}", "}", f"{idx}"])
      elem = etree.Element(tag_name, nsmap = nsmap)
      elem.text = main_config['channel']['itunes'][idx]
      channel.append(elem)

    # Dictionaries (nested)
    if isinstance(main_config['channel']['itunes'][idx], dict) == True:
      tag_ns = f"{main_config['feed']['xml']['namespaces']['itunes']}"
      tag_name = "".join(["{", f"{tag_ns}", "}", f"{idx}"])
      owner = etree.Element(tag_name, nsmap = nsmap)
      for sidx in main_config['channel']['itunes'][idx]:
        tag_ns = f"{main_config['feed']['xml']['namespaces']['itunes']}"
        tag_name = "".join(["{", f"{tag_ns}", "}", f"{sidx}"])
        selem = etree.Element(tag_name, nsmap = nsmap)
        selem.text = main_config['channel']['itunes'][idx][sidx]
        owner.append(selem)

      channel.append(owner)

    # Lists
    if isinstance(main_config['channel']['itunes'][idx], list) == True:
      tag_ns = f"{main_config['feed']['xml']['namespaces']['itunes']}"
      tag_name = "".join(["{", f"{tag_ns}", "}", f"{idx}"])
      category = etree.Element(tag_name, nsmap = nsmap)
      for sidx in main_config['channel']['itunes'][idx]:
        selem = etree.Element(tag_name, nsmap = nsmap)
        selem.text = str(sidx)
        category.append(selem)

      channel.append(category)

    # Booleans
    if isinstance(main_config['channel']['itunes'][idx], bool) == True:
      tag_ns = f"{main_config['feed']['xml']['namespaces']['itunes']}"
      tag_name = "".join(["{", f"{tag_ns}", "}", f"{idx}"])
      selem = etree.Element(tag_name, nsmap = nsmap)
      if main_config['channel']['itunes'][idx] == True:
        selem.text = 'yes'
      else:
        selem.text = 'no'

      channel.append(selem)

  for idx in main_config['channel']['podcast'].keys():
    print(idx, main_config['channel']['podcast'][idx])

    # Strings
    if isinstance(main_config['channel']['podcast'][idx], str) == True:
      tag_ns = f"{main_config['feed']['xml']['namespaces']['podcast']}"
      tag_name = "".join(["{", f"{tag_ns}", "}", f"{idx}"])
      elem = etree.Element(tag_name, nsmap = nsmap)
      elem.text = main_config['channel']['podcast'][idx]
      channel.append(elem)

    # Dictionaries (nested)
    if isinstance(main_config['channel']['podcast'][idx], dict) == True:
      tag_ns = f"{main_config['feed']['xml']['namespaces']['podcast']}"
      tag_name = "".join(["{", f"{tag_ns}", "}", f"{idx}"])
      owner = etree.Element(tag_name, nsmap = nsmap)
      for sidx in main_config['channel']['podcast'][idx]:
        tag_ns = f"{main_config['feed']['xml']['namespaces']['podcast']}"
        tag_name = "".join(["{", f"{tag_ns}", "}", f"{sidx}"])
        selem = etree.Element(tag_name, nsmap = nsmap)

        if isinstance(main_config['channel']['podcast'][idx][sidx], str) == True:
          selem.text = str(main_config['channel']['podcast'][idx][sidx])

        if isinstance(main_config['channel']['podcast'][idx][sidx], bool) == True:
          if main_config['channel']['podcast'][idx][sidx] == True:
            selem.text = 'yes'
          else:
            selem.text = 'no'
        

        owner.append(selem)

      channel.append(owner)

    # Lists
    if isinstance(main_config['channel']['podcast'][idx], list) == True:
      tag_ns = f"{main_config['feed']['xml']['namespaces']['podcast']}"
      tag_name = "".join(["{", f"{tag_ns}", "}", f"{idx}"])
      category = etree.Element(tag_name, nsmap = nsmap)
      for sidx in main_config['channel']['podcast'][idx]:
        selem = etree.Element(tag_name, nsmap = nsmap)
        selem.text = str(sidx)
        category.append(selem)

      channel.append(category)

    # Booleans
    if isinstance(main_config['channel']['podcast'][idx], bool) == True:
      tag_ns = f"{main_config['feed']['xml']['namespaces']['podcast']}"
      tag_name = "".join(["{", f"{tag_ns}", "}", f"{idx}"])
      selem = etree.Element(tag_name, nsmap = nsmap)
      if main_config['channel']['podcast'][idx] == True:
        selem.text = 'yes'
      else:
        selem.text = 'no'

      channel.append(selem)


  # Close Channel

  # Render Item blocks

    # Iterate and load episodes dynamically


  # Close RSS

  # Write to file
  print(etree.tostring(rss, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode())


if __name__ == '__main__':
  main()
