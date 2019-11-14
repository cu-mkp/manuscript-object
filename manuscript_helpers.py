import os
import re
import pandas as pd
from collections import OrderedDict
from typing import List, Union, Optional, Dict
from recipe import Recipe

properties = ['animal', 'body_part', 'currency', 'definition',
              'environment', 'material', 'medical', 'measurement',
              'music', 'plant', 'place', 'personal_name',
              'profession', 'sensory', 'tool', 'time', 'weapon']

def process_file(filename, version) -> List[Recipe]:
  """
  Open and read file in /ms-xml/. Creates a dict of the form identity: entry, which is returned and
  added to a larger dictionary of the same format.

  Inputs:
    filename: str -- the name of the file including path from the current directory.
    version: str -- denotes the version of the manuscript in use, either tc, tcn, or tl.
  Output:
    entries: List[Recipe] -- a List containing every entry in the manuscript.
  """
  entries = OrderedDict()
  with open(filename, 'r') as f:
    text = re.sub(r'\s+', ' ', f.read())
    divs = re.findall(r'(<div (continues="yes" )?id="(.*?)" categories="([\w\s;]*)"( margin="[-\w]*")?( continued="yes")?>(.*?)</div>)', text)
    if divs:
      for div in divs:
        identity, entry = div[2], div[0]
        if identity in entries.keys():
          entries[identity] = f'{entries[identity]}\n\n{entry}'
        else:
          entries[identity] = entry
  return entries

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

def generate_complete_manuscript(apply_corrections=True):
  entries = OrderedDict()
  versions = {'tc': {}, 'tcn': {}, 'tl': {}} # Each as (id: entry) in inner dict
  identities = []

  for version in versions.keys():
    file_dict = {}
    dir_path = os.getcwd() + f'/../m-k-manuscript-data/ms-xml/{version}/'
    for r, d, f in os.walk(dir_path):
      for filename in f: # iterate through /ms-xml/ folder
        file_id = filename.split('_')[1]
        entry_dict = process_file(f'{dir_path}{filename}', version)
        for identity, entry in entry_dict.items():
          file_dict[f'{file_id};{identity}'] = entry

    file_dict = OrderedDict(sorted(file_dict.items(), key=lambda x: x[0])) # sort filedict by key
    entry_dict = OrderedDict()

    for combined_id, entry in file_dict.items():
      file_id, identity = combined_id.split(';')
      if identity in entry_dict.keys():
        entry_dict[identity] = f'{entry_dict[identity]}\n\n{entry}'
      else:
        entry_dict[identity] = entry
        identities.append(identity)
  
    versions[version] = entry_dict
  
  identities = list(set(identities))
  identities.sort()

  for identity in identities:
    tc = versions['tc'].get(identity, '')
    tcn = versions['tcn'].get(identity, '')
    tl = versions['tl'].get(identity, '')

    entries[identity] = Recipe(identity, tc, tcn, tl)

  if apply_corrections:
    entries = use_thesaurus(entries)

  return entries
