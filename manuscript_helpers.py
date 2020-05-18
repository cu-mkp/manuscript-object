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

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'
m_k_data_to_thesaurus = f'{m_path}/manuscript-object/thesaurus'

def use_thesaurus(entries: Dict[str, Recipe]) -> List[Recipe]:
  """
  Use /thesaurus/ to standardize the vocabulary in the manuscript. If the thesaurus does not exist,
  create it. Read in the thesaurus for each property, iterate through the manuscript, and apply
  corrections to any words in the manuscript also found in the thesaurus. Code to handle manual
  corrections to the thesaurus is included, but commented out until data is included.

  Input:
    entries: List[Recipe] -- A list containing the entries of the manuscript as members of the
                             Recipe class.
  Output:
    entries: List[Recipe] -- same as above, but with the thesaurus corrections applied.
  """
  if not os.path.exists(m_k_data_to_thesaurus):
    print('Thesaurus not found. Generating now.')
    os.system(f'python {cwd}/manuscript-object/thesaurus.py')
    print('Finished Generating Thesaurus')

  # manual_corrections = pd.read_csv('manual_vocab.csv')

  for prop in properties:
    dct = {} # {verbatim_term: prefLabel_en}
    df = pd.read_csv(f'{m_k_data_to_thesaurus}/{prop}.csv')

    # manual_df = manual_corrections[manual_corrections['property'] == prop]
    # manual_dict = {} # verbatim_term, prefLabel_en pairs

    # for _, row in manual_df.iterrows():
    #   manual_dict[row.verbatim_term] = row.prefLabel_en

    for i, row in df.iterrows(): # add corrections to a dictionary for O(1) access later on.
      if row.verbatim_term != row.prefLabel_en and isinstance(row.prefLabel_en, str):
        # dct[row.verbatim_term] =  manual_dict.get(row.verbatim_term) if row.verbatim_term in manual_dict.keys() else row.prefLabel_en
        dct[row.verbatim_term] = row.prefLabel_en

    for identity, entry in entries.items(): # iterate through the manuscript.
      for j, term in enumerate(entry.properties[prop]['tl']):
        entry.properties[prop]['tl'][j] = dct.get(term, term) # apply corrections if needed.
      entry.properties[prop]['tl'] = list(set(entry.properties[prop]['tl'])) # remove duplicates
      entries[identity] = entry
  return entries

def process_file(filepath: str) -> OrderedDict[str, str]:
  """
  Open the file, and separate each div. If a div is broken up into different parts or across
  multiple folio pages, they are attached.
  Inputs:
    filepath: string representing the filepath of the file to be read in /ms-text/[version]
  Outputs:
    entries: a dictionary containing the text of each entry keyed by folio and div IDs.
  """

  entries = OrderedDict()
  # read file, extract text and folio ID
  with open(filepath, encoding="utf-8", errors="surrogateescape") as f:
    text = f.read()
    folio = filepath.split('/')[-1].split('_')[1][1:] # .../tl_p162v_preTEI.xml -> 162v

    text = text.replace('\n', '**NEWLINE**') # re.findall cannot scan over newlines.
    divs = re.findall(r'(<div([\w\s=";-]*)>(.*?)</div>)', text) # separate text by divs
    if divs:
      for i, div in enumerate(divs): # iterate through divs
        attributes = div[1] # text within div tag, between second parentheses in the regex.
        identity = re.findall(r'id="p([\w_]*)"', attributes) # find identity
        identity = identity[0] if identity else '' # unpack identity from regex
        key = f'{folio};{identity}' # create unique key for attaching 'continued' entries.
        if key in entries.keys(): # if this div is a part of another entry, attach them
          new_text = div[0].replace('**NEWLINE**', '\n').replace('\n\n\n', '\n\n')
          entries[key] = entries[key] + "\n\n" + new_text
        else: # otherwise create a new entry in the entries dict.
          entries[key] = div[0].replace('**NEWLINE**', '\n').replace('\n\n\n', '\n\n')
  return entries

def generate_complete_manuscript(apply_corrections=True) -> Dict[str, Recipe]:
  """
  Generate complete manuscript by extracting the text from each folder in /m-k-manuscript-data/ms-xml/
  Apply corrections if specified.

  Inputs:
    None
  Outputs:
    entries: A dictionary of Recipe objects keyed by div ID.
  """
  entries = OrderedDict() # initialize dict to return. identity: entry object/Recipe Class
  versions = OrderedDict({'tc': {}, 'tcn': {}, 'tl': {}}) # holds contents of each folder before combined

  """
  Iterate through each folder in /ms-xml/. Use process_file() to locate divs
  keyed by div and folio ID. Accumulate these dicts to entry_dict, sort it, and save it to the
  version dict keyed by version.

  TODO: Instead of going version by version, consider going folio by folio.
  """
  for version in versions:
    dir_path = f'{m_path}/ms-xml/{version}/'
    entry_dict = OrderedDict()

    for r, d, f in os.walk(dir_path):
      for filename in f: # iterate through /ms-xml/{version} folder
        # split folio by entry
        info: OrderedDict[str, str] = process_file(f'{dir_path}{filename}')
        for identity, text in info.items(): # add each entry to dictionary
          entry_dict[identity] = text

    entry_dict = OrderedDict(sorted(entry_dict.items(), key=lambda x: x[0])) # sort entry_dict by key
    versions[version] = entry_dict # save entry dict in the versions dict

  """
  Since all the dicts should have the same keys, iterate through one, and recall the text in each
  version. If the entry continues another, attach it to the previous entry, otherwise, generate a
  new Recipe object and save it to the 'entries' dict keyed by div ID.
  """
  for identity in versions['tc'].keys():
    folio, entry_id = identity.split(';')
    tc, tcn, tl = [x.get(identity).strip() for x in versions.values()]
    if entry_id in entries.keys():
      old = entries[entry_id]
      entries[entry_id] = Recipe(entry_id, old.folio,
                                 old.versions['tc'] + '\n\n' + tc,
                                 old.versions['tcn'] + '\n\n' + tcn,
                                 old.versions['tl'] + '\n\n' + tl,)
    else:
      entries[entry_id] = Recipe(entry_id, folio, tc, tcn, tl)

  # if specified, manually rewrite entry properties based on thesaurus.
  if apply_corrections:
    entries = use_thesaurus(entries)

  return entries

def common_element(list1: List[str], list2: List[str]) -> bool:
  """
  Used in the search function to compare list of keywords to a list of properties
  Inputs:
    list1: a list of strings representing the search keywords
    list2: a list of string representing the properties of an entry
  Outputs:
    bool: True if they share a common element. Otherwise, False
  """
  for x in list1:
    for y in list2:
      if x == y:
        return True
  return False
