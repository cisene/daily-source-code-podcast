#!/usr/bin/env python3
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen

ANGLE = -7.886
CENTRE = (432, 352)
SIZE = 820
NAVY = '#392e7a'
WHITE = '#ffffff'
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf'
NARROW = '/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf'

BANDS = [(114, 129, 751, 255), (114, 449, 751, 575)]
DAILY = [('D', (134, 152, 228, 226)), ('A', (263, 148, 341, 225)), ('I', (398, 152, 454, 227)), ('L', (515, 152, 577, 227)), ('Y', (647, 152, 725, 227))]
SOURCE = [('S', (123, 273, 201, 430)), ('O', (225, 275, 304, 430)), ('U', (338, 275, 418, 429)), ('R', (447, 274, 529, 427)), ('C', (560, 273, 639, 428)), ('E', (669, 277, 741, 430))]
GROW_DAILY = 2.0
GROW_SOURCE = 3.5
CODE = [('C', (149, 472, 249, 549)), ('O', (307, 473, 411, 551)), ('D', (467, 472, 569, 548)), ('E', (627, 474, 712, 550))]


def glyph(font, char, box):
  glyphs = font.getGlyphSet()
  name = font.getBestCmap()[ord(char)]
  bounds = BoundsPen(glyphs)
  glyphs[name].draw(bounds)
  gx0, gy0, gx1, gy1 = bounds.bounds
  x0, y0, x1, y1 = box
  sx, sy = (x1 - x0) / (gx1 - gx0), (y1 - y0) / (gy1 - gy0)
  pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip('0').rstrip('.'))
  glyphs[name].draw(TransformPen(pen, (sx, 0, 0, -sy, x0 - gx0 * sx, y0 + gy1 * sy)))
  return pen.getCommands()


def shrink(box, g):
  x0, y0, x1, y1 = box
  return (x0 + g, y0 + g, x1 - g, y1 - g)


def rounded(x0, y0, x1, y1, r):
  return f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="{r:.1f}"/>'


def squareLetter(char, box):
  x0, y0, x1, y1 = box
  w, h = x1 - x0, y1 - y0
  stem, bar = (0.31 if char == 'E' else 0.24) * w, 0.24 * h
  outer, inner = 0.15 * h, 0.04 * h
  body, cuts = [], []
  if char == 'D':
    body.append(f'<path d="M{x0},{y0} H{x1 - outer} Q{x1},{y0} {x1},{y0 + outer} V{y1 - outer} Q{x1},{y1} {x1 - outer},{y1} H{x0} Z"/>')
  elif char == 'E':
    body.append(rounded(x0, y0, x1, y1, inner))
  else:
    body.append(rounded(x0, y0, x1, y1, outer))
  if char in 'OCD':
    cuts.append(rounded(x0 + stem, y0 + bar, x1 - stem, y1 - bar, inner))
  if char == 'C':
    cuts.append(f'<rect x="{x1 - stem - 1:.1f}" y="{y0 + 0.36 * h:.1f}" width="{stem + 2:.1f}" height="{0.28 * h:.1f}"/>')
  if char == 'E':
    notch = 0.14 * h
    for top in (0.29 * h, 0.71 * h - notch):
      cuts.append(f'<rect x="{x0 + stem:.1f}" y="{y0 + top:.1f}" width="{w - stem + 1:.1f}" height="{notch:.1f}"/>')
  return body, cuts


def main():
  if not 2 <= len(sys.argv) <= 4:
    print('Usage: art-logo-2004.py OUT.svg [ASPECT [SCALE]]')
    sys.exit(2)
  num, _, den = (sys.argv[2] if len(sys.argv) > 2 else '1/1').partition('/')
  scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
  height = SIZE * scale
  width = height * float(num) / float(den or 1)
  serif, narrow = TTFont(SERIF), TTFont(NARROW)
  bands = ''.join(f'<rect x="{a}" y="{b}" width="{c - a}" height="{d - b}"/>' for a, b, c, d in BANDS)
  daily = ' '.join(glyph(serif, c, shrink(box, GROW_DAILY)) for c, box in DAILY)
  source = ' '.join(glyph(narrow, c, shrink(box, GROW_SOURCE)) for c, box in SOURCE)
  body, cuts = [], []
  for c, box in CODE:
    b, k = squareLetter(c, box)
    body += b
    cuts += k
  x0, y0 = CENTRE[0] - width / 2, CENTRE[1] - height / 2
  svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:g} {y0:g} {width:g} {height:g}" width="{width:g}" height="{height:g}">
  <title>Daily Source Code (logo of 2004-09, reconstructed)</title>
  <rect x="{x0:g}" y="{y0:g}" width="{width:g}" height="{height:g}" fill="{WHITE}"/>
  <g transform="rotate({ANGLE} {CENTRE[0]} {CENTRE[1]})">
    <g fill="{NAVY}">{bands}</g>
    <path fill="{WHITE}" stroke="{WHITE}" stroke-width="{2 * GROW_DAILY}" stroke-linejoin="round" d="{daily}"/>
    <path fill="{NAVY}" stroke="{NAVY}" stroke-width="{2 * GROW_SOURCE}" stroke-linejoin="round" d="{source}"/>
    <g fill="{WHITE}">{''.join(body)}</g>
    <g fill="{NAVY}">{''.join(cuts)}</g>
  </g>
</svg>
'''
  with open(sys.argv[1], 'w') as fp:
    fp.write(svg)


if __name__ == '__main__':
  main()
