""" Data transform to generate a folder of .json files containing properties and the entries that contain them. """
# Python Modules
import os
import re
from typing import Dict, Tuple, List

# Third Party Modules
import pandas as pd
from tqdm import tqdm

# Local Modules
from digital_manuscript import BnF
from recipe import Recipe

properties = ['animal', 'body_part', 'currency', 'definition', 'environment', 'material',
              'medical', 'measurement', 'music', 'plant', 'place', 'personal_name',
              'profession', 'sensory', 'tool', 'time', 'weapon']

def read_csvs() -> Dict[str, pd.DataFrame]:
  """
  Read thesaurus file and save keyed by property.
  Input: None
  Output: df_dict -- a dict where they keys are an element of properties and the value is the thesaurus
  DataFrame for that property.
  """
  df_dict = {}
  for prop in properties:
    df = pd.read_csv(f'thesaurus/{prop}.csv')
    # add new column containing empty lists to store entries
    df['entries'] = df.apply(lambda x: [], axis=1)
    df_dict[prop] = df
  return df_dict

def read_manuscript(manuscript: BnF, df_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
  """
  Iterate through the manuscript and each row in each of the DataFrames. Add entry identities to rows
  for properties that entry has.

  Input: manuscript -- The complete BnF Ms 640 digital manuscript.
  Output: df_dict -- a dict where they keys are an element of properties and the value is the thesaurus
  DataFrame for that property.
  """
  for identity in tqdm(manuscript.entries.keys()):
    entry = manuscript.entries[identity]
    for prop in properties:
      df = df_dict[prop]
      prop_list = entry.get_prop(prop, 'tl')
      for j, row, in df.iterrows():
        if any(term == row.verbatim_term for term in prop_list):
          entry_list = row.entries.copy()
          entry_list.append(entry)
          df.loc[j] = [row.freq, row.verbatim_term, row.prefLabel_en, entry_list.copy()]
          df_dict[prop] = df
  return df_dict

def df_to_dict(df = pd.DataFrame) -> Dict[str, Tuple[Reciple, str]]:
  """
  Convert dataframe into dict of the following format:
  'prefLabel_en1': [(entry1, verbatim_term1), (entry2, verbatim_term2), ...],
  'prefLabel_en2: [(entry3, verbatim_term3), ...], ...

  Inputs: df -- dataframe contianing columns 'prefLabel_en', 'verbatim_term', and 'entries'
  Outputs: prop_dict 
  """
  prop_dict = {}
  for _, row in df.iterrows():
    for entry in row.entries:
      info_list = prop_dict.get(row.prefLabel_en, [])
      info_list.append((entry, row.verbatim_term))
      prop_dict[row.prefLabel_en] = info_list.copy()
  return prop_dict

def write_json(prop_dict, prop: str) -> None:
  text = '{\n'
  for term, info_list in prop_dict.items():
    text += f'  "{term}": [\n'
    for info_tuple in info_list:
      entry, verbatim_term = info_tuple
      iden, title = entry.identity, entry.title['tl'].strip()

      text += '    {\n'
      text += f'    "verbatim_term": "{verbatim_term}",\n'
      text += f'    "entry_id": "{iden}",\n'
      text += f'    "entry_title": "{title}"\n'
      text += '    },\n'
    text += "  ],\n"
  text += '}'

  text = re.sub(r',\n  ]', '\n  ]', text) # remove inner trailing commas
  text = re.sub(r'],\n}', ']\n}', text) # remove outer trailing commas

  f = open(f"jsons/{prop}.json", "w") # save to a file in /jsons/
  f.write(text)
  f.close() 

def write_csv(prop_dict, prop: str) -> None: 
  f = open(f'properties/{prop}.csv', "w")
  f.write('prefLabel_en,verbatim_term,identity,title\n')

  for term, info_list in prop_dict.items():
    for info_tuple in info_list:
      entry, verbatim_term = info_tuple
      iden, title = entry.identity, entry.title['tl']
      f.write(f'{term},{verbatim_term},{iden},{title}\n')
  f.close()

def write_files(df_dict) -> None:
  """
  Write each dataframe to a JSON of the following format. Create a new DataFrame with one entry per row and save
  it as a .csv.
  {
    term1: {
      "entry1": "title1",
      "entry2": "title2",
      ...
    },
    ...
  }

  Input: df_dict -- a dict where they keys are an element of properties and the value is the thesaurus
  DataFrame for that property.
  Output: None
  """
  for prop, df in df_dict.items():
    prop_dict = df_to_dict(df)
    write_json(prop_dict, prop)
    write_csv(prop_dict, prop)

def jsonify():
  """ Controller for the file. Match entries to properties and write files. """

  # Check for prerequesite files
  if not os.path.exists('thesaurus'):
    print('Thesaurus not found. Generating now.')
    os.system('python thesaurus.py')

  # Check for folders to write to
  for folder in ['jsons', 'properties']:
    if not os.path.exists(folder):
      os.mkdir(folder)

  manuscript = BnF(apply_corrections=False)
  df_dict = read_csvs() # read in thesaurus
  df_dict = read_manuscript(manuscript, df_dict) # match entries to terms
  write_files(df_dict) # write jsons and csvs

jsonify()
