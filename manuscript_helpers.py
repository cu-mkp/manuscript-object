import os
import re
import pandas as pd
from collections import OrderedDict
from typing import List, Union, Optional, Dict, OrderedDict
from recipe import Recipe

properties = ['animal', 'body_part', 'currency', 'definition',
              'environment', 'material', 'medical', 'measurement',
              'music', 'plant', 'place', 'personal_name',
              'profession', 'sensory', 'tool', 'time', 'weapon']

def use_thesaurus(entries: Dict[str, Recipe]) -> List[Recipe]:
  """
  Use /thesaurus/ to standardize the vocabulary in the manuscript. If the thesaurus does not exist,
  create it. Read in the thesaurus for each property, iterate through the manuscript, and apply
  corrections to any words in the manuscript also found in the thesaurus.

  Input:
    entries: List[Recipe] -- A list containing the entries of the manuscript as members of the
                             Recipe class.
  Output:
    entries: List[Recipe] -- same as above, but with the thesaurus corrections applied.
  """
  if not os.path.exists('thesaurus'):
    print('Thesaurus not found. Generating now.')
    os.system('python thesaurus.py')
    print('Finished Generating Thesaurus')

  for prop in properties:
    dct = {} # {verbatim_term: prefLabel_en}
    df = pd.read_csv(f'thesaurus/{prop}.csv')
    for i, row in df.iterrows(): # add corrections to a dictionary for O(1) access later on.
      if row.verbatim_term != row.prefLabel_en:
        dct[row.verbatim_term] = row.prefLabel_en

    for identity, entry in entries.items(): # iterate through the manuscript.
      for j, term in enumerate(entry.properties[prop]['tl']):
        entry.properties[prop]['tl'][j] = dct.get(term, term) # apply corrections if needed.
      entry.properties[prop]['tl'] = list(set(entry.properties[prop]['tl'])) # remove duplicates
      entries[identity] = entry
    return entries

def process_file(filepath: str) -> OrderedDict[str, str]:
  entries = OrderedDict()
  with open(filepath, encoding="utf-8", errors="surrogateescape") as f:
    text = f.read()
    clean_text = re.sub(r'\s+', ' ', text)
    folio = filepath.split('/')[-1].split('_')[1][1:]

    # needs to be done line by line
    divs = re.findall(r'(<div([\w\s=";-]*)>(.*?)</div>)', clean_text)
    if divs:
      for i, div in enumerate(divs):
        attributes = div[1]
        identity = re.findall(r'id="p([\w_]*)"', attributes)
        identity = identity[0] if identity else ''
        key = f'{folio};{identity}'
        entries[key] = div[2]
  return entries

def generate_complete_manuscript(apply_corrections=True):
  """

  """
  entries = OrderedDict() # initialize dict to return. identity: entry object
  versions = OrderedDict({'tc': {}, 'tcn': {}, 'tl': {}}) # holds contents of each folder before combined

  for version in versions: # iterate through each folder in /m-k-manuscript-data/ms-xml/
    dir_path = os.getcwd() + f'/../m-k-manuscript-data/ms-xml/{version}/'
    entry_dict = OrderedDict()

    for r, d, f in os.walk(dir_path):
      for filename in f: # iterate through /ms-xml/{version} folder
        # split folio by entry
        info: OrderedDict[str, str] = process_file(f'{dir_path}{filename}')
        for identity, text in info.items(): # add each entry to dictionary
          entry_dict[identity] = text

    entry_dict = OrderedDict(sorted(entry_dict.items(), key=lambda x: x[0])) # sort entry_dict by key
    versions[version] = entry_dict # save entry dict in the versions dict
  
  for identity in versions['tc'].keys():
    folio, entry_id = identity.split(';')
    tc, tcn, tl = [x.get(identity) for x in versions.values()]
    if entry_id in entries.keys():
      old = entries[entry_id]
      entries[entry_id] = Recipe(entry_id, old.folio,
                                 old.versions['tc'] + '\n\n' + tc,
                                 old.versions['tcn'] + '\n\n' + tcn,
                                 old.versions['tl'] + '\n\n' + tl,)
    else:
      entries[entry_id] = Recipe(entry_id, folio, tc, tcn, tl)

  if apply_corrections:
    entries = use_thesaurus(entries)

  return entries
