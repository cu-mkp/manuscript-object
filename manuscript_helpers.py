import os
import re
import pandas as pd
from typing import List, Union, Optional
from recipe import Recipe

properties = ['animal', 'body_part', 'currency', 'definition',
              'environment', 'material', 'medical', 'measurement',
              'music', 'plant', 'place', 'personal_name',
              'profession', 'sensory', 'tool', 'time']

def file_to_entries_all(file_obj) -> List[str]:
  """ Divide file into each of its entries """
  entries = []
  entry: str = ''
  adding = False
  for line in file_obj.readlines():
    if 'div' in line:
      adding = True
      entry = ''
    elif '/div' in line:
      adding = False
      entries.append(re.sub(r'\s+', ' ', entry))
    elif adding:
      entry = f'{entry} {line}'
  return entries

def package_entries_all(versions, version, entries):
  """ extract id and save to version dict for {version}_all.xml """
  for entry in entries:
    id_search = re_id.search(entry)
    identity = id_search[0] if id_search else ''
    identity = re_tags.sub('', identity)
    versions[version][identity] = entry
  return versions

def process_file(filename, version, continuing_entries) -> List[Recipe]:
  """ Open and read file in /ms-xml/ """
  entries = {}
  with open(filename, 'r') as f:
    text = re.sub(r'\s+', ' ', f.read())
    divs = re.findall(r'<div (continues="yes" )?id="(.*?)"( margin="[-\w]*")?( continued="yes")?>(.*?)</div>', text)
    if divs:
      for div in divs:
        identity, entry = div[1], div[4] 
        if div[0] != '': # if the entry continues another
          old_entry = continuing_entries.get(identity, '')
          continuing_entries[identity] = f'{old_entry}{entry}'
        else:
          entries[identity] = entry
  return entries, continuing_entries

def generate_complete_manuscript(complete=True, apply_corrections=True):
  entries = []
  versions = {'tc': {}, 'tcn': {}, 'tl': {}} # Each as (id: entry) in inner dict
  identities = []

  for version in versions.keys():
    if complete: # use {version}_all.xml
      file_path = directory + 'all_' + version + '.xml'
      with open(file_path, 'r') as f:
        entries = file_to_entries_all(f)
        versions = package_entries_all(versions, version, entries)
    else: # use /ms-xml/
      dir_path = os.getcwd() + f'/../m-k-manuscript-data/ms-xml/{version}/'
      continuing_entries = {} # initialize dict of entries marked with continues="yes"
      for r, d, f in os.walk(dir_path):
        for filename in f: # iterate through folder
          entry_dict, continuing_entries = process_file(f'{dir_path}{filename}', version, continuing_entries)
          for identity, entry in entry_dict.items(): # add to version_dict
            versions[version][identity] = entry
            identities.append(identity) # keep list of all ids
      for identity, entry in continuing_entries.items():
        entry_beginning = versions[version][identity] # get old entry
        versions[version][identity] = f'{entry_beginning} {entry}' # append and reinsert
  
  identities = list(set(identities)) # remove duplicates
  identities.sort()
  for identity in identities:
    tc = versions['tc'].get(identity, '')
    tcn = versions['tcn'].get(identity, '')
    tl = versions['tl'].get(identity, '')

    # if not tc or not tcn or not tl:
    #   print(identity, not tc, not tcn, not tl)
    
    entries.append(Recipe(identity, tc, tcn, tl))

  if apply_corrections:
    if not os.path.exists('thesaurus'):
      print('Thesaurus not found. Generating now.')
      os.system('python thesaurus.py')
      print('Finished Generating Thesaurus')

    for prop in properties: # generate correction_dict from thesaurus
      dct = {}
      df = pd.read_csv(f'thesaurus/{prop}.csv')
      for i, row in df.iterrows(): # add corrections to a dictionary for O(1) access
        if row.verbatim_term != row.prefLabel_en:
          dct[row.verbatim_term] = row.prefLabel_en

      for entry in entries:
        for i, term in enumerate(entry.properties[prop]['tl']):
          new_term = dct.get(term, None)
          if new_term:
            entry.properties[prop]['tl'][i] = new_term
        entry.properties[prop]['tl'] = list(set(entry.properties[prop]['tl']))
  
  return entries