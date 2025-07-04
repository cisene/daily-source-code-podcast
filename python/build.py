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

APPLICATION_NAME = 'MirrorBallLawnmower'
APPLICATION_VERSION = '0.1'


def writeRSS(filepath, contents):
  s = "\n".join(contents) + "\n"
  with open(filepath, "w") as f:
    f.write(contents)


def writeYAML(filepath, contents):
  pass

def truefalseTOyesno(booleanvalue):
  if booleanvalue == True:
    result = "Yes"
  else:
    result = "No"

  return result


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

  for tag in main_config['rss']['channel']['tags']:
    tag_tagname = None
    tag_namespace = None
    tag_text = None
    tag_ns = None
    tag_elem = None

    tag_tagname = tag['tag']

    if "namespace" in tag:
      tag_namespace = tag['namespace']

      if tag_namespace == "atom":
        tag_ns = main_config['feed']['xml']['namespaces']['atom']

      if tag_namespace == "dc":
        tag_ns = main_config['feed']['xml']['namespaces']['dc']

      if tag_namespace == "itunes":
        tag_ns = main_config['feed']['xml']['namespaces']['itunes']

      if tag_namespace == "podcast":
        tag_ns = main_config['feed']['xml']['namespaces']['podcast']

    if tag_ns != None:
      tag_elem = "".join(["{", f"{tag_ns}", "}", f"{tag_tagname}"])
    else:
      tag_elem = "".join([f"{tag_tagname}"])

    elem = etree.Element(tag_elem, nsmap = nsmap)

    if "attributes" in tag:
      for attr in tag['attributes']:
        elem.set(attr, str(tag['attributes'][attr]))

    if "text" in tag:
      tag_text = tag['text']
      if isinstance(tag_text, bool) == True:
        if tag_text == True:
          elem.text = 'yes'
        else:
          elem.text = 'no'
      else:
        elem.text = str(tag_text)

    if "tags" in tag:
      for subtag in tag['tags']:
        subtag_tagname = None
        subtag_namespace = None
        subtag_text = None
        subtag_ns = None
        subtag_elem = None

        subtag_tagname = subtag['tag']

        if "namespace" in subtag:
          subtag_namespace = subtag['namespace']

          if subtag_namespace == "atom":
            subtag_ns = main_config['feed']['xml']['namespaces']['atom']

          if subtag_namespace == "dc":
            subtag_ns = main_config['feed']['xml']['namespaces']['dc']

          if subtag_namespace == "itunes":
            subtag_ns = main_config['feed']['xml']['namespaces']['itunes']

          if subtag_namespace == "podcast":
            subtag_ns = main_config['feed']['xml']['namespaces']['podcast']

        if subtag_ns != None:
          subtag_elem = "".join(["{", f"{subtag_ns}", "}", f"{subtag_tagname}"])
        else:
          subtag_elem = "".join([f"{subtag_tagname}"])

        subelem = etree.Element(subtag_elem, nsmap = nsmap)

        if "attributes" in subtag:
          for attr in subtag['attributes']:
            subelem.set(attr, str(subtag['attributes'][attr]))

        if "text" in subtag:
          subtag_text = subtag['text']
          if isinstance(subtag_text, bool) == True:
            #subelem.text = subtag_text
            if subtag_text == True:
              subelem.text = 'yes'
            else:
              subelem.text = 'no'
          else:
            subelem.text = str(subtag_text)
        elem.append(subelem)

    channel.append(elem)
  # Close Channel

  # Add generator tag
  elem = etree.Element("generator", nsmap = nsmap)
  elem.text = f"{APPLICATION_NAME}/{APPLICATION_VERSION}"
  channel.append(elem)

  # Render Item blocks
  for episode in reversed(main_config['episodes']):

    # Iterate and load episodes dynamically
    episode_path = f"{ITEMS_PATH}{episode}"
    print(episode_path)
    item = readYAML(episode_path)
    #print(item)

    elem_item = etree.Element("item", nsmap = nsmap)

    if item['title'] != None:
      elem_title = etree.Element("title", nsmap = nsmap)
      elem_title.text = str(item['title'])
      elem_item.append(elem_title)

    if item['pubDate'] != None:
      elem_pubdate = etree.Element("pubDate", nsmap = nsmap)
      elem_pubdate.text = str(item['pubDate'])
      elem_item.append(elem_pubdate)

    if item['author'] != None:
      elem_author = etree.Element("author", nsmap = nsmap)
      elem_author.text = str(item['author'])
      elem_item.append(elem_author)

    if item['link'] != None:
      elem_link = etree.Element("link", nsmap = nsmap)
      elem_link.text = str(item['link'])
      elem_item.append(elem_link)
    
    if item['category'] != None:
      elem_category = etree.Element("category", nsmap = nsmap)
      elem_category.text = str(item['category'])
      elem_item.append(elem_category)

    if item['language'] != None:
      elem_language = etree.Element("language", nsmap = nsmap)
      elem_language.text = str(item['language'])
      elem_item.append(elem_language)

    if item['description'] != None:
      elem_description = etree.Element("description", nsmap = nsmap)
      elem_description.text = str(item['description'])
      elem_item.append(elem_description)

    if item['guid'] != None:
      elem_guid = etree.Element("guid", nsmap = nsmap)
      elem_guid.set("isPermaLink", str(item['guid']['isPermaLink']))
      elem_guid.text = str(item['guid']['link'])
      elem_item.append(elem_guid)

    if item['enclosure'] != None:
      elem_enclosure = etree.Element("enclosure", nsmap = nsmap)

      if item['enclosure']['type'] != None:
        elem_enclosure.set("type", str(item['enclosure']['type']))

      if item['enclosure']['length'] != None:
        elem_enclosure.set("length", str(item['enclosure']['length']))

      if item['enclosure']['url'] != None:
        elem_enclosure.set("url", str(item['enclosure']['url']))

      elem_item.append(elem_enclosure)

    if "itunes" in item:
      tag_ns = main_config['feed']['xml']['namespaces']['itunes']
      for tag in item['itunes'].keys():
        if item['itunes'][tag] == None:
          continue

        tag_tagname = tag
        tag_elem = "".join(["{", f"{tag_ns}", "}", f"{tag_tagname}"])

        itunes_elem = etree.Element(tag_elem, nsmap = nsmap)

        if isinstance(item['itunes'][tag], list) == True:
          print("itunes: list element")


        if isinstance(item['itunes'][tag], dict) == True:
          for attr in item['itunes'][tag]:
            itunes_elem.set(attr, str(item['itunes'][tag][attr]))

        if isinstance(item['itunes'][tag], str) == True:
          itunes_elem.text = str(item['itunes'][tag])

        if isinstance(item['itunes'][tag], int) == True:
          itunes_elem.text = str(item['itunes'][tag])

        if isinstance(item['itunes'][tag], bool) == True:
          if item['itunes'][tag] == True:
            itunes_elem.text = 'yes'
          else:
            itunes_elem.text = 'no'

        elem_item.append(itunes_elem)

    if "podcast" in item:
      tag_ns = main_config['feed']['xml']['namespaces']['podcast']
      for tag in item['podcast'].keys():

        # Skip null values
        if item['podcast'][tag] == None:
          continue

        skip_tags = [
          'images'
        ]
        if tag in skip_tags:
          continue

        tag_tagname = tag
        tag_elem = "".join(["{", f"{tag_ns}", "}", f"{tag_tagname}"])
        #print(tag, type(item['podcast'][tag]))

        podcast_elem = etree.Element(tag_elem, nsmap = nsmap)

        if isinstance(item['podcast'][tag], list) == True:
          print("podcast: list element")
          print(item['podcast'][tag], tag)

          if tag == "person":
            person_attributes = [
              'href',
              'img',
              'group',
              'role',
            ]

            for person in item['podcast'][tag]:
              tag_tagname = tag
              tag_elem = "".join(["{", f"{tag_ns}", "}", f"{tag_tagname}"])

              podcast_elem.text = str(person['person'])

              for attr in person_attributes:
                if attr in person:
                  if person[attr] != None:
                    podcast_elem.set(attr, str(person[attr]))

          if tag == "socialInteract":
            si_attributes = [
              'protocol',
              'uri',
              'accountId',
              'accountUrl'
            ]
            for siAccount in item['podcast'][tag]:
              if siAccount['protocol'] == 'disabled':
                podcast_elem.set('protocol', str(siAccount['protocol']))
              else:
                for attr in si_attributes:
                  podcast_elem.set(attr, str(siAccount[attr]))

          if tag == "chapters":
            # <podcast:chapters url="https://example.com/episode1/chapters.json" type="application/json+chapters" />
            ch_attributes = [
              'url',
              'type',
            ]
            for chapt in item['podcast'][tag]:
              if chapt['url'] != None and chapt['type'] != None:
                for attr in ch_attributes:
                  podcast_elem.set(attr, chapt[attr])

          if tag == "alternateEnclosure":
            # <podcast:alternateEnclosure type="audio/mpeg" length="2490970" bitrate="160707.74">
            #   <podcast:source uri="https://example.com/file-0.mp3" />
            #   <podcast:source uri="ipfs://QmdwGqd3d2gFPGeJNLLCshdiPert45fMu84552Y4XHTy4y" />
            #   <podcast:source uri="https://example.com/file-0.torrent" contentType="application/x-bittorrent" />
            #   <podcast:source uri="http://example.onion/file-0.mp3" />
            # </podcast:alternateEnclosure>

            # [
            #   {
            #     'type': 'audio/mpeg',
            #     'length': 9455188,
            #     'bitrate': 56000,
            #     'default': True,
            #     'title': 'Daily Source Code',
            #     'source': {
            #       'uri': 'http://cloud2.urj.nl/bt/dailySourceCode-20040813-112954-082.mp3'}
            #   }
            # ]


            ae_attributes = [
              'type',
              'length',
              'bitrate',
              'default',
              'title',
            ]

            for ae in item['podcast'][tag]:
              print(ae)
              if ae['source'] != None:
                for attr in ae_attributes:
                  if ae[attr] != None:
                    podcast_elem.set(attr, str(ae[attr]))

                if isinstance(ae['source'], dict) == True:
                  tag_tagname = "source"
                  tag_elem = "".join(["{", f"{tag_ns}", "}", f"{tag_tagname}"])
                  source_elem = etree.Element(tag_elem, nsmap = nsmap)
                  source_elem.set('uri', str(ae['source']['uri']))
                  podcast_elem.append(source_elem)

        if isinstance(item['podcast'][tag], dict) == True:
          #print("podcast: dict element")
          #print(item['podcast'][tag], tag)

          for attr in item['podcast'][tag]:
            if item['podcast'][tag][attr] != None:
              podcast_elem.set(attr, str(item['podcast'][tag][attr]))

        if isinstance(item['podcast'][tag], str) == True:
          if item['podcast'][tag] != None:
            podcast_elem.text = str(item['podcast'][tag])

        if isinstance(item['podcast'][tag], int) == True:
          podcast_elem.text = str(item['podcast'][tag])

        if isinstance(item['podcast'][tag], bool) == True:
          if item['podcast'][tag] == True:
            podcast_elem.text = 'yes'
          else:
            podcast_elem.text = 'no'

        elem_item.append(podcast_elem)


    rss.append(elem_item)
  # Close RSS

  # Write to file
  rss_contents = etree.tostring(rss, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode()
  print(rss_contents)
  writeRSS(RSS_PATH, rss_contents)

if __name__ == '__main__':
  main()
