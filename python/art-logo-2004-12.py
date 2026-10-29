#!/usr/bin/env python3
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.basePen import AbstractPen

SIZE = 680
SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'

SLABS = [
  {'word': 'DAILY', 'face': [(90, 138), (612, 108), (612, 268), (90, 256)], 'u': (0.11, 0.77), 'v': (0.09, 0.93), 'fill': ('#8a5cc6', '#6a3fa6'), 'top': '#b79be0'},
  {'word': 'SOURCE', 'face': [(130, 272), (610, 282), (610, 440), (130, 386)], 'u': (0.0, 0.82), 'v': (0.06, 0.92), 'fill': ('#f4f2f6', '#9c9aa0'), 'top': '#ffffff'},
  {'word': 'CODE', 'face': [(100, 372), (600, 428), (595, 592), (100, 500)], 'u': (0.16, 0.70), 'v': (0.24, 0.98), 'fill': ('#7f52bd', '#5a3496'), 'top': '#a786d6'},
]
DEPTH = 9
EXTRUDE = (-1.0, 0.45)
TOP_DEPTH = 10


def homography(quad):
  (x0, y0), (x1, y1), (x2, y2), (x3, y3) = quad
  dx1, dx2, dx3 = x1 - x2, x3 - x2, x0 - x1 + x2 - x3
  dy1, dy2, dy3 = y1 - y2, y3 - y2, y0 - y1 + y2 - y3
  den = dx1 * dy2 - dx2 * dy1
  g = (dx3 * dy2 - dx2 * dy3) / den
  h = (dx1 * dy3 - dx3 * dy1) / den
  a, b, c = x1 - x0 + g * x1, x3 - x0 + h * x3, x0
  d, e, f = y1 - y0 + g * y1, y3 - y0 + h * y3, y0
  def apply(u, v):
    w = g * u + h * v + 1
    return ((a * u + b * v + c) / w, (d * u + e * v + f) / w)
  return apply


class MapPen(AbstractPen):
  def __init__(self, pen, fn):
    self.pen, self.fn = pen, fn

  def moveTo(self, p):
    self.pen.moveTo(self.fn(*p))

  def lineTo(self, p):
    self.pen.lineTo(self.fn(*p))

  def curveTo(self, *ps):
    self.pen.curveTo(*[self.fn(*p) for p in ps])

  def qCurveTo(self, *ps):
    self.pen.qCurveTo(*[None if p is None else self.fn(*p) for p in ps])

  def closePath(self):
    self.pen.closePath()

  def endPath(self):
    self.pen.endPath()

  def addComponent(self, name, transform):
    self.pen.addComponent(name, transform)


def wordPath(font, slab, offset=(0, 0)):
  glyphs = font.getGlyphSet()
  cmap = font.getBestCmap()
  cap = font['OS/2'].sCapHeight
  names = [cmap[ord(c)] for c in slab['word']]
  width = sum(glyphs[n].width for n in names)
  (u0, u1), (v0, v1) = slab['u'], slab['v']
  project = homography(slab['face'])
  pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.2f}".rstrip('0').rstrip('.'))
  mapped = MapPen(pen, lambda x, y: tuple(c + o for c, o in zip(project(x, y), offset)))
  x = 0
  for n in names:
    t = ((u1 - u0) / width, 0, 0, -(v1 - v0) / cap, u0 + x * (u1 - u0) / width, v1)
    glyphs[n].draw(TransformPen(mapped, t))
    x += glyphs[n].width
  return pen.getCommands()


def points(pts):
  return ' '.join(f"{x:.1f},{y:.1f}" for x, y in pts)


def main():
  if len(sys.argv) != 2:
    print('Usage: art-logo-2004-12.py OUT.svg')
    sys.exit(2)
  font = TTFont(SERIF)
  defs, slabs, words = [], [], []
  for i, s in enumerate(SLABS):
    tl, tr, br, bl = s['face']
    defs.append(f'<linearGradient id="face{i}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{s["fill"][0]}"/><stop offset="1" stop-color="{s["fill"][1]}"/></linearGradient>')
    top = [tl, tr, (tr[0] - TOP_DEPTH, tr[1] - TOP_DEPTH * 0.6), (tl[0] + TOP_DEPTH * 0.2, tl[1] - TOP_DEPTH * 0.6)]
    slabs.append(f'<polygon fill="{s["top"]}" points="{points(top)}"/><polygon fill="url(#face{i})" points="{points(s["face"])}"/>')
    sides = ''.join(f'<path d="{wordPath(font, s, (EXTRUDE[0] * k, EXTRUDE[1] * k))}"/>' for k in range(DEPTH, 0, -1))
    words.append(f'<g fill="#1d1724">{sides}</g><path fill="url(#silver)" stroke="#2a2330" stroke-width="0.8" d="{wordPath(font, s)}"/>')
  defs.append('<linearGradient id="silver" x1="0" y1="0" x2="0.35" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset="0.55" stop-color="#e4e1ea"/><stop offset="1" stop-color="#b9b4c2"/></linearGradient>')
  svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}">
  <title>Daily Source Code (logo by Marchel, 2004-12, reconstructed)</title>
  <defs>{''.join(defs)}</defs>
  <rect width="{SIZE}" height="{SIZE}" fill="#ffffff"/>
  {''.join(slabs)}
  {''.join(words)}
</svg>
'''
  with open(sys.argv[1], 'w') as fp:
    fp.write(svg)


if __name__ == '__main__':
  main()
