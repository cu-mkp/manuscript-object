import os
import re
import pandas as pd
from typing import List, Union, Optional
from recipe import Recipe
from manuscript_helpers import generate_complete_manuscript

class BnF():

  complete_manuscript = generate_complete_manuscript(complete=False)

  def __init__(self, entry_list = []):
    """ Initialize entire manuscript. If a list of IDs is given, narrow it down to them. """
    if entry_list:
      self.entries = [page for page in BnF.complete_manuscript.copy() if page.identity in entry_list]
    else:
      self.entries = BnF.complete_manuscript.copy()

  def entry(self, identity: str):
    """ Return entry with the given identity. """
    for entry in self.entries:
      if entry.identity == identity:
        return entry

  search_type = Optional[Union[str, bool]]
  def search(self, animal: search_type = None, body_part: search_type = None, currency: search_type = None,
             definition: search_type = None, environment: search_type = None, material: bool = None,
             medical: search_type = None, measurement: search_type = None, music: search_type = None,
             plant: search_type = None, place: search_type = None, personal_name: search_type = None,
             profession: search_type = None, sensory: search_type = None, tool: search_type = None,
             time: search_type = None) -> List[str]:
    """
    Search through each entry and return the identities that satisfy the criterion. Arguments are each of the element
    types for a manuscript entry, which can be a string, bool, or None. If the argument is a string, then results must have
    an element that matches that string. If the argument is a bool, then the results must have at least one of those element
    types. If the argument is None, it does not effect the search.
    """

    args = {'animal': animal, 'body_part': body_part, 'currency': currency, 'definition': definition,
            'environment': environment, 'material': material, 'medical': medical, 'measurement': measurement,
            'music': music, 'plant': plant, 'place': place, 'personal_name': personal_name, 'profession': profession,
            'sensory': sensory, 'tool': tool, 'time': time}

    versions = ['tc', 'tcn', 'tl']
    results = self.entries # initialize results
    search_bools = [k for k, v in args.items() if isinstance(v, bool)] # select bool element categories
    search_strings = [k for k, v in args.items() if isinstance(v, str)] # select string element categories

    for s in search_bools: # filter by each bool
      results = [r for r in results if any(r.get_attribute(s, v) for v in versions)]
    for s in search_strings: # filter by each string
      results = [r for r in results if any(args[s] in r.get_attribute(s, v) for v in versions)]
  
    return([r.identity for r in results]) # return identities

  def tablefy(self):
    # id, head, no. words, category, amount of each tag, margins
    # include figure margins?
    df = pd.DataFrame(columns=['entry'], data=self.entries)
    df['identity'] = df.entry.apply(lambda x: x.identity)
    df['title'] = df.entry.apply(lambda x: x.title['tl'])
    df['length'] = df.entry.apply(lambda x: x.length['tl'])
    df['num_materials'] = df.entry.apply(lambda x: len(x.attributes['material']['tl']))
    df['margins'] = df.entry.apply(lambda x: len(x.margins))
    df['del_tags'] = df.entry.apply(lambda x: len(x.del_tags))
    df = df.drop(columns=['entry'])
    return df
