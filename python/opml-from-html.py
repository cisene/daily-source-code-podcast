#!/usr/bin/python
# -*- coding: utf-8 -*-

# Reconstructs OPML show notes from their HTML rendering:
# - Radio UserLand's activeRenderer (blognewsnetwork.com/members/0000001/outlines/),
#   it keeps the structure, the text of every node and the url of link and rss
#   nodes, and loses the other attributes (artist, album, type="song", f,
#   sizeFile, whenFileCreated) and the #title directive.
# - OmniOutliner's HTML export (mp3.dailysourcecode.podshow.com/DSC-NNN-YYYY-MM-DD/index.html),
#   it keeps the structure and the text, links written "Link <url>" in the OPML.
#
# Usage: opml-from-html.py <outline.html> [<outline.opml>]
#        opml-from-html.py --compare <outline.html> <original.opml>

import re
import sys
import html

from datetime import datetime


NODE = re.compile(r'<div id="r(\d+)" class="active(\d+)">(.*?)<span id="t\1">(.*?)</span></td></tr></table>', re.S)
TITLE = re.compile(r'<p class="activeTitle">(.*?)</p>', re.S)
UPDATED = re.compile(r'last updated:\s*([^<]+?)\s*</div>', re.S)
HREF = re.compile(r'<a [^>]*href="([^"]*)"')
RSSCLUDE = re.compile(r"(?:rssclude|transclude)\('p\d+',\s*'([^']*)'\)")

# The renderer linked bare urls and email addresses, the OPML has them as text
AUTOLINK = re.compile(r'<a href="(?:mailto:)?([^"<>]+)">\1</a>')

# Radio on the Mac wrote MacRoman bytes into OPML declared ISO-8859-1. The
# renderer read them as MacRoman and wrote an entity, or a name for the
# characters it had no entity for.
MACROMAN_NAMES = {
  '[sgl dagger]': '\u2020',
  '[dbl dagger]': '\u2021',
  '[pi]': '\u03c0',
  '[^]': '\u02c6',
  '[greater equal]': '\u2265',
  '[less equal]': '\u2264',
  '[delta]': '\u2206',
  '[infinity]': '\u221e',
  "[base ']": '\u201a',
}

# Radio left NUL characters at the end of some texts (also in its own OPML),
# XML has no way to write them
CONTROL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
ENTITY = re.compile(r'&(?:[A-Za-z][A-Za-z0-9]*|#\d+|#x[0-9A-Fa-f]+);')


def encodingOf(data):
  # Radio wrote Latin-1, OmniOutliner UTF-8 and says so
  head = data[:2000].decode('latin-1').lower()
  return 'utf-8' if 'charset=utf-8' in head or 'encoding="utf-8"' in head else 'latin-1'


def readText(path):
  with open(path, 'rb') as fp:
    data = fp.read()
  return data.decode(encodingOf(data), errors='replace')


def decodeText(value):
  # Back from the rendered html to the text of the OPML node, as Latin-1
  value = AUTOLINK.sub(r'\1', value)
  for name, char in MACROMAN_NAMES.items():
    value = value.replace(name, char)

  def entity(m):
    # &nbsp; and the other ASCII entities are part of the text itself
    char = html.unescape(m.group(0))
    if len(char) == 1 and ord(char) > 127 and char != '\xa0':
      return char
    return m.group(0)

  value = ENTITY.sub(entity, value)
  out = []
  for char in value:
    if ord(char) > 255:
      try:
        char = char.encode('mac_roman').decode('latin-1')
      except UnicodeEncodeError:
        pass
    elif ord(char) > 127 and char != '\xa0':
      try:
        char = char.encode('mac_roman').decode('latin-1')
      except UnicodeEncodeError:
        pass
    out.append(char)
  return ''.join(out)


def parseHTML(text):
  # Returns (title, updated, nodes), nodes are dicts with text, url, type, children
  title = TITLE.search(text)
  updated = UPDATED.search(text)
  root = {'children': []}
  stack = [(0, root)]
  last = None
  # Node ids are a page prefix and a counter from 0: r90, r91 .. r99, r910
  first = NODE.search(text)
  prefix = first.group(1)[:-1] if first and first.group(1).endswith('0') else ''
  for m in NODE.finditer(text):
    number = int(m.group(1)[len(prefix):])
    depth = int(m.group(2))
    wedge = m.group(3)
    if last != None and number > last[0] + 1:
      # Empty nodes were not rendered, but they used up a node number. A blank
      # line belongs with the node before it unless the next node is deeper.
      blank = depth if depth > last[1] else last[1]
      while stack[-1][0] >= blank:
        stack.pop()
      for _ in range(number - last[0] - 1):
        stack[-1][1]['children'].append({'text': '', 'children': [], 'blank': True})
    last = (number, depth)
    node = {'text': decodeText(m.group(4)), 'children': []}
    rss = RSSCLUDE.search(wedge)
    href = HREF.search(wedge)
    if rss:
      node['type'] = 'link'
      node['url'] = html.unescape(rss.group(1))
    elif href and not href.group(1).startswith('javascript:'):
      node['type'] = 'link'
      node['url'] = html.unescape(href.group(1))
    while stack[-1][0] >= depth:
      stack.pop()
    stack[-1][1]['children'].append(node)
    stack.append((depth, node))
  return (
    html.unescape(title.group(1)).strip() if title else None,
    updated.group(1).strip() if updated else None,
    root['children'],
    'activeRenderer',
  )


# A row ends with the two tables around its cells, an attachment can bring its
# own table. The last row of a page can run into Adam's Amazon iframes.
OMNI_TOKEN = re.compile(r'<!-- Begin group [^>]*-->|<!-- End group [^>]*-->|<td style="[^"]*" class="subcell col1">(.*?)(?:</td>\s*</tr>\s*</table>\s*</td>\s*</tr>\s*</table>\s*</div>|<br>\s*(?=<iframe))', re.S)
OMNI_LINK = re.compile(r'<span><a href="([^"]*)">(.*?)</a></span>', re.S)
# Attached audio: an inline QuickTime player titled with the file name
OMNI_PLAYER = re.compile(r'<table [^>]*display: inline;[^>]*>.*?<div [^>]*>(.*?)</div>.*?</object>(?:\s*</td>\s*</tr>\s*</table>)?', re.S)
# Other attachments: a grey link to the file
OMNI_ATTACHMENT = re.compile(r'<span style="background-color: #f1f1f1;"><a href="[^"]*">(.*?)</a></span>', re.S)


def decodeOmniText(value):
  value = re.sub(r'\s*<br>\s*$', '', value)
  value = OMNI_PLAYER.sub(r'\1', value)
  value = OMNI_ATTACHMENT.sub(r'\1', value)
  value = OMNI_LINK.sub(lambda m: f"{m.group(2)} <{m.group(1)}>", value)
  # Styled runs (colors) have no counterpart in the OPML
  value = re.sub(r'<span style="[^"]*">|</span>', '', value)
  value = re.sub(r'<br>\n?', "\n", value)
  return html.unescape(value)


def parseOmniHTML(text):
  root = {'children': []}
  stack = [root]
  last = None
  for m in OMNI_TOKEN.finditer(text):
    token = m.group(0)
    if token.startswith('<!-- Begin group'):
      stack.append(last)
    elif token.startswith('<!-- End group'):
      stack.pop()
    else:
      last = {'text': decodeOmniText(m.group(1)), 'children': []}
      stack[-1]['children'].append(last)
  title = re.search(r'<title>(.*?)</title>', text, re.S)
  return (html.unescape(title.group(1)).strip() if title and title.group(1).strip() else None, None, root['children'], 'OmniOutliner')


def parseAny(text):
  if 'class="subcell col1"' in text:
    return parseOmniHTML(text)
  return parseHTML(text)


def parseOPML(text):
  # Tolerant reader for Radio's OPML, which is not always well-formed XML
  root = {'children': []}
  stack = [root]
  for m in re.finditer(r'<outline\b((?:[^>"]|"[^"]*")*?)(/?)>|</outline>', text):
    if m.group(0) == '</outline>':
      stack.pop()
      continue
    attrs = {k: html.unescape(v) for k, v in re.findall(r'(\w+)="([^"]*)"', m.group(1))}
    node = dict(attrs, children=[])
    stack[-1]['children'].append(node)
    if m.group(2) != '/':
      stack.append(node)
  return root['children']


def quoteAttribute(value):
  value = CONTROL.sub('', value)
  return value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def writeOutlines(nodes, depth, lines):
  for node in nodes:
    attrs = f'text="{quoteAttribute(node["text"])}"'
    if node.get('type') != None:
      attrs += f' type="{node["type"]}" url="{quoteAttribute(node["url"])}"'
    indent = "\t" * depth
    if len(node['children']) == 0:
      lines.append(f'{indent}<outline {attrs}/>')
    else:
      lines.append(f'{indent}<outline {attrs}>')
      writeOutlines(node['children'], depth + 1, lines)
      lines.append(f'{indent}\t</outline>')


def renderOPML(title, updated, nodes, source, encoding, renderer):
  lines = []
  lines.append(f'<?xml version="1.0" encoding="{"UTF-8" if encoding == "utf-8" else "ISO-8859-1"}"?>')
  if renderer == 'activeRenderer':
    lost = 'Only text, structure and link urls survive the rendering, the other attributes (artist, album, type="song", f, sizeFile, whenFileCreated) and #title are lost, NUL characters are left out.'
  else:
    lost = 'Only text and structure survive the rendering, links are written "text <url>" as in the OmniOutliner OPML of the same period.'
  lines.append(f'<!-- Reconstructed from the {renderer} HTML {quoteAttribute(source)} by python/opml-from-html.py. {lost} -->')
  lines.append('<opml version="1.1">')
  lines.append('\t<head>')
  lines.append(f'\t\t<title>{quoteAttribute(title or "")}.opml</title>')
  if updated != None:
    # Radio wrote this in Adam's local time, kept as it was rendered
    lines.append(f'\t\t<!-- last updated: {quoteAttribute(updated)} -->')
  lines.append('\t\t<ownerName>Adam Curry</ownerName>')
  lines.append('\t\t</head>')
  lines.append('\t<body>')
  writeOutlines(nodes, 2, lines)
  lines.append('\t\t</body>')
  lines.append('\t</opml>')
  return "\n".join(lines) + "\n"


def flatten(nodes, depth=0, out=None):
  # (depth, text, url) of every node, the #directives of the OPML left out
  if out == None:
    out = []
  for node in nodes:
    if node.get('text', '').startswith('#'):
      continue
    out.append((depth, node.get('text'), node.get('url')))
    flatten(node['children'], depth + 1, out)
  return out


def normalizeText(value):
  return re.sub(r'\s+', ' ', value or '').strip()


def compare(html_path, opml_path):
  _, _, rendered, _ = parseAny(readText(html_path))
  original = parseOPML(readText(opml_path))
  a = flatten(rendered)
  b = flatten(original)
  differences = 0
  for i in range(max(len(a), len(b))):
    x = a[i] if i < len(a) else None
    y = b[i] if i < len(b) else None
    if x == None or y == None or x[0] != y[0] or normalizeText(x[1]) != normalizeText(y[1]) or (x[2] or None) != (y[2] or None):
      differences += 1
      if differences <= 10:
        print(f"  node {i}: html {x}\n          opml {y}")
  print(f"{html_path}: {len(a)} nodes from html, {len(b)} in opml, {differences} differ")
  return differences


def main():
  if len(sys.argv) == 4 and sys.argv[1] == '--compare':
    sys.exit(1 if compare(sys.argv[2], sys.argv[3]) > 0 else 0)
  if len(sys.argv) not in [2, 3]:
    print(__doc__ or 'Usage: opml-from-html.py <outline.html> [<outline.opml>]')
    sys.exit(2)
  with open(sys.argv[1], 'rb') as fp:
    encoding = encodingOf(fp.read())
  title, updated, nodes, renderer = parseAny(readText(sys.argv[1]))
  source = sys.argv[1].split('/')[-1]
  if title == None:
    title = re.sub(r'\.html?$', '', source)
  opml = renderOPML(title, updated, nodes, source, encoding, renderer)
  if len(sys.argv) == 3:
    with open(sys.argv[2], 'wb') as fp:
      fp.write(opml.encode(encoding, errors='xmlcharrefreplace'))
  else:
    sys.stdout.write(opml)


if __name__ == '__main__':
  main()
