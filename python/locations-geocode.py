#!/usr/bin/env python3
import os
import re
import sys
import json
import math

GEONAMES_DIR = os.path.expanduser('~/.cache/geonames/')
HOME_COUNTRIES = ['US', 'GB', 'NL', 'BE']
MIN_MENTIONS = 2
SPELLINGS = {'gilford': 'Guildford', 'guilford': 'Guildford', 'gilford surrey': 'Guildford', 'skippal': 'Schiphol', 'schipol': 'Schiphol', 'vegas': 'Las Vegas', 'the netherlands': 'Netherlands', 'the united states': 'United States', 'the united kingdom': 'United Kingdom', 'the uk': 'UK', 'the us': 'US', 'nyc': 'New York City', 'sf': 'San Francisco', 'l.a.': 'Los Angeles', 'la': 'Los Angeles', 'cali': 'California', 'atlantic': 'Atlantic Ocean', 'pacific': 'Pacific Ocean', 'new york': 'New York City', 'ny': 'New York City',
  'u.s': 'US', 'u.s.': 'US', 'u.k': 'UK', 'u.k.': 'UK', 'd.c': 'Washington DC', 'dc': 'Washington DC', 'l.a': 'Los Angeles', 'san fran': 'San Francisco', 'ca': 'California', 'nocal': 'Northern California', 'socal': 'Southern California',
  'g-town': 'Guildford', 'isle of white': 'Isle of Wight', 'straussburg': 'Strasbourg', 'gary street': 'Geary Street', 'london heathrow': 'Heathrow Airport', 'heathrow': 'Heathrow Airport', 'sfo': 'San Francisco International Airport', 'flanders belgium': 'Flanders', 'philly': 'Philadelphia', 'b.c': 'British Columbia', 'san francisco bay area': 'Bay Area', 'holland': 'Netherlands', 'the holland': 'Netherlands',
  'al': 'Alabama', 'ak': 'Alaska', 'az': 'Arizona', 'ar': 'Arkansas', 'co': 'Colorado', 'ct': 'Connecticut', 'fl': 'Florida', 'ga': 'Georgia', 'il': 'Illinois', 'ia': 'Iowa', 'ks': 'Kansas', 'ky': 'Kentucky', 'md': 'Maryland', 'mi': 'Michigan', 'mn': 'Minnesota', 'mo': 'Missouri', 'nc': 'North Carolina', 'nj': 'New Jersey', 'nv': 'Nevada', 'oh': 'Ohio', 'ok': 'Oklahoma', 'pa': 'Pennsylvania', 'sc': 'South Carolina', 'tn': 'Tennessee', 'tx': 'Texas', 'ut': 'Utah', 'va': 'Virginia', 'vt': 'Vermont', 'wa': 'Washington', 'wi': 'Wisconsin'}
STOP = {'earth', 'metro', 'delta', 'sierra', 'charlie', 'delta sierra', 'east coast', 'west coast', 'jersey', 'heaven', 'hell', 'paradise', 'mars', 'moon', 'the moon', 'internet', 'web', 'pod', 'podcast', 'source code', 'daily source code', 'adam', 'curry', 'dsc', 'north', 'south', 'east', 'west', 'midwest', 'middle east', 'downtown', 'uptown', 'land', 'city', 'town', 'island', 'world', 'nation', 'state', 'states', 'kingdom', 'republic', 'empire', 'union', 'continent', 'broadway', 'main street', 'wall street', 'high street',
  'linux', 'youtube', 'skype', 'skypeing', 'wi-fi', 'voip', 'isp', 'firewire', 'macbook', 'craigslist', 'nielsen', 'earthlink', 'google earth', 'paris hilton', 'christ', 'eagles', 'black eyed peas', 'billy ocean', 'frankie valley', 'charlotte church', 'sim city', 'eurovision', 'comic strip', 'la la la', 'la, la', 'rock, rock', 'rock, rock, rock', 'quakers', 'yankee', 'east enders', 'jersey joe', 'podshow', 'potcho', 'podjo', 'potcha', 'zedcast', 'dsc3', 'gamesweasel', 'chicken five', 'koma 1000', 'i river', 'subdupt', 'sincel', 'ferrox', 'tvo', 'yorkie', 'stick', 'rock white', 'bilbatore', 'san seo', 'san', 'gile pems', 'pinkland', 'potio plus', 'expo', 'university', 'college radio', 'nielsen', 'virgin atlantic', 'america west', 'kentucky derby', 'roman empire', 'united states of europe', 'boulevard of broken dreams', 'wonderland', 'podshow suckless zone music', 'pod show island', 'apple store', 'food bar'}
OVERRIDES = {'south beach': 6946365, 'surrey': 2636512, 'yorkshire': 2633349, 'essex': 2649889, 'suffolk': 2636561, 'kent': 3333158, 'sussex': 2636510, 'west sussex': 2634258, 'east sussex': 2650328, 'hampshire': 2647554, 'cornwall': 2652355, 'devon': 2651292, 'berkshire': 2655856, 'oxfordshire': 2640726, 'norfolk': 2641455, 'lancashire': 2644974, 'middlesex': 2642605}
SHORT = {'UK', 'US', 'USA', 'NYC', 'DC', 'UAE', 'EU'}
LOW_CODES = {'ADM2', 'ADM3', 'ADM4', 'ADM5', 'ADMD', 'PPLX'}

AREA_CODES = {'PCLI', 'PCLD', 'PCLS', 'PCLF', 'PCLIX', 'PCL', 'TERR', 'ADM1', 'ADM2', 'ADMD', 'RGN', 'CONT', 'ISLS', 'ISL', 'PPLC', 'PPLA', 'PPLA2'}
LOC_CODES = AREA_CODES | {'MTS', 'MT', 'PK', 'VAL', 'DSRT', 'PEN', 'BAY', 'SEA', 'OCN', 'LK', 'STM', 'GULF', 'STRT', 'CHN', 'CAPE', 'BCH', 'PRK', 'RESV', 'AREA'}
FAC_CODES = {'AIRP', 'AIRF', 'HTL', 'STDM', 'BLDG', 'MUS', 'UNIV', 'SCH', 'CSTL', 'PAL', 'TOWR', 'BDG', 'MNMT', 'THTR', 'OPRA', 'CTRS', 'SQR', 'PRK', 'MALL', 'ZOO', 'AMUS', 'RSTN', 'PRT', 'MKT', 'HSP', 'CH', 'CTHL', 'STNB', 'ANS', 'HSTS', 'GDN', 'RECG', 'RSRT', 'CSNO', 'PIER', 'HBR', 'MAR', 'CMP', 'MILB', 'INSM', 'AIRB', 'PS', 'TNL', 'DAM', 'LTHSE', 'ISL', 'ISLS', 'AREA', 'PPLX'}
KIND = {'A': 3, 'P': 2, 'L': 1, 'T': 1, 'H': 1, 'S': 0, 'V': 0, 'R': 0, 'U': 0}


def fits(label, fclass, fcode, population):
  if label in ['GPE', 'LOC'] and fclass == 'P':
    return population > 0 or fcode in AREA_CODES
  if label == 'GPE':
    return fcode in AREA_CODES
  if label == 'LOC':
    return fcode in LOC_CODES
  if label == 'FAC':
    return fcode in FAC_CODES or (fclass == 'P' and population > 0)
  return False


def isPlaceName(name):
  return name[:1].isupper() and name.lower() not in STOP and (len(name) > 3 or name in SHORT) and not re.search(r'\.(com|org|net)\b', name, re.I)


def main():
  with open(sys.argv[1]) as fp:
    entities = json.load(fp)
  for wrong, right in SPELLINGS.items():
    for name in [n for n in entities if n.lower() == wrong]:
      target = entities.setdefault(right, {'files': {}})
      for k, v in entities.pop(name).items():
        if k == 'files':
          for fn, c in v.items():
            target['files'][fn] = target['files'].get(fn, 0) + c
        else:
          target[k] = target.get(k, 0) + v
  with open(sys.argv[1].replace('.json', '-merged.json'), 'w') as fp:
    json.dump(entities, fp, ensure_ascii=False)
  names = {}
  for name, entry in entities.items():
    mentions = sum(v for k, v in entry.items() if k != 'files')
    if mentions >= MIN_MENTIONS and isPlaceName(name):
      names.setdefault(name.lower(), []).append(name)

  alternates = {}
  with open(GEONAMES_DIR + 'alternateNamesV2.txt', encoding='utf-8') as fp:
    for line in fp:
      f = line.split('\t')
      if f[2] in ['', 'en', 'abbr'] and f[3].lower() in names:
        alternates.setdefault(f[1], set()).add(f[3].lower())

  candidates = {}
  with open(GEONAMES_DIR + 'allCountries.txt', encoding='utf-8') as fp:
    for line in fp:
      f = line.rstrip('\n').split('\t')
      keys = {f[1].lower(), f[2].lower()} | alternates.get(f[0], set())
      hits = [k for k in keys if k in names]
      if not hits:
        continue
      place = {
        'geonames': int(f[0]), 'name': f[1], 'ascii': f[2].lower(), 'latitude': float(f[4]), 'longitude': float(f[5]),
        'class': f[6], 'code': f[7], 'country': f[8], 'admin1': f[10],
        'population': int(f[14] or 0), 'alternates': len(f[3].split(',')) if f[3] else 0, 'elevation': int(f[15]) if f[15] else None, 'dem': int(f[16]) if f[16] else None,
      }
      for k in hits:
        candidates.setdefault(k, []).append(place)

  result = {}
  for key, spellings in names.items():
    labels = {}
    files = {}
    for s in spellings:
      for k, v in entities[s].items():
        if k == 'files':
          for fn, c in v.items():
            files[fn] = files.get(fn, 0) + c
        else:
          labels[k] = labels.get(k, 0) + v
    label = max(labels, key=labels.get)
    fitting = [p for p in candidates.get(key, []) if fits(label, p['class'], p['code'], p['population'])]
    if not fitting:
      continue
    preferred = fitting
    if label == 'FAC':
      preferred = [p for p in preferred if p['class'] == 'S'] or preferred

    def score(p):
      s = math.sqrt(p['alternates'] + 1) * math.log10(p['population'] + 10) * (1.2 if p['country'] in HOME_COUNTRIES else 1)
      s *= 0.5 if p['code'] in LOW_CODES else 1
      s *= 1.5 if p['class'] == 'P' else 1
      s *= 3 if key in [p['name'].lower(), p['ascii']] or p['code'].startswith('PCL') else 1
      return (s, p['population'])
    best = next((p for p in candidates.get(key, []) if p['geonames'] == OVERRIDES.get(key)), None) or max(preferred, key=score)
    spelling = max(spellings, key=lambda s: sum(v for k, v in entities[s].items() if k != 'files'))
    result[spelling] = {'label': label, 'mentions': sum(labels.values()), 'files': len(files), 'place': best, 'alternatives': len(fitting) - 1}
  with open(sys.argv[2], 'w') as fp:
    json.dump(result, fp, indent=1, ensure_ascii=False)
  print(f"{len(names)} names mentioned {MIN_MENTIONS}+ times, {len(result)} found in GeoNames")


if __name__ == '__main__':
  main()
