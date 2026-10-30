#!/usr/bin/env python3
import os
import sys
import yaml
from xml.sax.saxutils import escape

CHANNEL = '../yaml/daily-source-code.yaml'
UPLOAD = '../yaml/upload.yaml'
EPISODE_DIR = '../yaml/episodes/'
PAGES = ['/', '/episodes.html']


def main():
  write = '--write' in sys.argv
  with open(CHANNEL) as fp:
    channel = yaml.safe_load(fp)
  base = str(channel['feed']['base_url']).rstrip('/')
  with open(UPLOAD) as fp:
    site_dir = os.path.join(yaml.safe_load(fp)['stage'], 'site')

  pages = PAGES + ['/' + channel['feed']['filename']]
  urls = [base + page for page in pages]
  for name in channel['episodes']:
    with open(EPISODE_DIR + name) as fp:
      link = yaml.safe_load(fp).get('link')
    if not link or not link.startswith(base + '/episodes/'):
      sys.exit(f"{name}: link is not an episode page on the site: {link}")
    urls.append(link)
  if len(set(urls)) != len(urls):
    sys.exit('duplicate urls')

  sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
  sitemap += [f"  <url><loc>{escape(url)}</loc></url>" for url in urls]
  sitemap.append('</urlset>')

  robots = ['User-agent: *',
            'Allow: /',
            '',
            f"Sitemap: {base}/sitemap.xml"]

  print(f"sitemap.xml: {len(urls)} urls ({len(pages)} pages + {len(urls) - len(pages)} episodes)")
  print('robots.txt:')
  print('\n'.join('  ' + line for line in robots))
  if not write:
    print(f"dry run (add --write to write into {site_dir})")
    return
  os.makedirs(site_dir, exist_ok=True)
  with open(os.path.join(site_dir, 'sitemap.xml'), 'w') as fp:
    fp.write('\n'.join(sitemap) + '\n')
  with open(os.path.join(site_dir, 'robots.txt'), 'w') as fp:
    fp.write('\n'.join(robots) + '\n')
  print(f"written to {site_dir}")


if __name__ == '__main__':
  main()
