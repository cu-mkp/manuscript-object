import os
import re
from typing import List
from recipe import Recipe


directory = os.getcwd() + '/../m-k-manuscript-data/allFolios/xml/'

re_entry = re.compile(r'<div>(.*?)</div>')
re_id = re.compile(r'<id>(.*?)</id>')
re_head = re.compile(r'<head>(.*?)</head>')
re_tags = re.compile(r'<.*?>')

attributes = ['animal', 'body_part', 'currency', 'definition', 'environment', 'material',
              'medical', 'measurement', 'music', 'plant', 'place', 'personal_name',
              'profession', 'sensory', 'tool', 'time']

class BnF():

  def __init__(self):
    self.entries = []

    versions = {'tc': {}, 'tcn': {}, 'tl': {}} # Each as (id: entry) in inner dict
    identities = []

    for version in versions.keys():
      file_path = directory + 'all_' + version + '.xml'
      with open(file_path, 'r') as f:
        text = self.clean_text(re.sub(r'\s+', ' ', f.read()))
        entries = re_entry.findall(text)
        for entry in entries:
          id_search = re_id.search(entry)
          identity = id_search[0] if id_search else ''
          identity = re_tags.sub('', identity)
          identities.append(identity)

          versions[version][identity] = entry

    identities = list(set(identities)) # remove duplicates
    for identity in identities:
      tc = versions['tc'].get(identity, '')
      tcn = versions['tcn'].get(identity, '')
      tl = versions['tl'].get(identity, '')
      
      self.entries.append(Recipe(identity, tc, tcn, tl))

  def entry(self, identity: str):
    for entry in self.entries:
      if entry.identity == identity:
        return entry

  def clean_text(self, text: str) -> str:
    figure_ids = re.findall(r'<id>(fig_.{1,8})</id>', text)
    for fig_id in figure_ids:
        text.replace(f'<id>{fig_id}</id>', f'<fid>{fig_id}</fid>')
    return text

  def search_any(self, animal: bool = None, body_part: bool = None, currency: bool = None, definition: bool = None, environment: bool = None,
             material: bool = None, medical: bool = None, measurement: bool = None, music: bool = None, plant: bool = None, place: bool = None,
             personal_name: bool = None, profession: bool = None, sensory: bool = None, tool: bool = None, time: bool = None):
    args = {'animal': animal, 'body_part': body_part, 'currency': currency, 'definition': definition,
            'environment': environment, 'material': material, 'medical': medical, 'measurement': measurement,
            'music': music, 'plant': plant, 'place': place, 'personal_name': personal_name, 'profession': profession,
            'sensory': sensory, 'tool': tool, 'time': time}
    versions = ['tc', 'tcn', 'tl']
    results = self.entries

    search = [k for k, v in args.items() if v is not None]
    for s in search:
      results = [r for r in results if any(r.get_attribute(s, v) for v in versions)]
    return([r.identity for r in results])

  def search_exact(self, animal: str = None, body_part: str = None, currency: str = None, definition: str = None, environment: str = None,
             material: str = None, medical: str = None, measurement: str = None, music: str = None, plant: str = None, place: str = None,
             personal_name: str = None, profession: str = None, sensory: str = None, tool: str = None, time: str = None):
    args = {'animal': animal, 'body_part': body_part, 'currency': currency, 'definition': definition,
            'environment': environment, 'material': material, 'medical': medical, 'measurement': measurement,
            'music': music, 'plant': plant, 'place': place, 'personal_name': personal_name, 'profession': profession,
            'sensory': sensory, 'tool': tool, 'time': time}
    versions = ['tc', 'tcn', 'tl']
    results = self.entries

    search = [k for k, v in args.items() if v is not None]
    for s in search:
      results = [r for r in results if any(args[s] in r.get_attribute(s, v) for v in versions)]
    return([r.identity for r in results])
