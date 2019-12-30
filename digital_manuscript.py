import os
import re
import pandas as pd
from typing import List, Union, Optional
from recipe import Recipe
from manuscript_helpers import generate_complete_manuscript

class BnF():

  def __init__(self, entry_list = [], apply_corrections = True):
    """ Initialize entire manuscript. If a list of IDs is given, narrow it down to them. """
    complete_manuscript = generate_complete_manuscript(apply_corrections=apply_corrections)
    # complete_manuscript2 = generate_complete_manuscript2(apply_corrections=apply_corrections)
    if entry_list:
      self.entries = {i:e for i, e in complete_manuscript.items() if e.identity in entry_list}
    else:
      self.entries = complete_manuscript

  def entry(self, identity: str = ''):
    """ Return entry with the given identity. """
    return self.entries.get(identity)

  search_type = Optional[Union[str, bool]]
  def search(self, animal: search_type = None, body_part: search_type = None, currency: search_type = None,
             definition: search_type = None, environment: search_type = None, material: bool = None,
             medical: search_type = None, measurement: search_type = None, music: search_type = None,
             plant: search_type = None, place: search_type = None, personal_name: search_type = None,
             profession: search_type = None, sensory: search_type = None, tool: search_type = None,
             time: search_type = None, weapon: search_type = None) -> List[str]:
    """
    Search through each entry and return the identities that satisfy the criterion. Arguments are each of the element
    types for a manuscript entry, which can be a string, bool, or None. If the argument is a string, then results must have
    an element that matches that string. If the argument is a bool, then the results must have at least one of those element
    types. If the argument is None, it does not effect the search.
    """

    args = {'animal': animal, 'body_part': body_part, 'currency': currency, 'definition': definition,
            'environment': environment, 'material': material, 'medical': medical, 'measurement': measurement,
            'music': music, 'plant': plant, 'place': place, 'personal_name': personal_name, 'profession': profession,
            'sensory': sensory, 'tool': tool, 'time': time, 'weapon': weapon}

    versions = ['tc', 'tcn', 'tl']
    results = self.entries # initialize results
    search_bools = [k for k, v in args.items() if isinstance(v, bool)] # select bool element categories
    search_strings = [k for k, v in args.items() if isinstance(v, str)] # select string element categories

    for s in search_bools: # filter by each bool
      results = {i: r for i, r in results.items() if any(r.get_prop(s, v) for v in versions)}
    for s in search_strings: # filter by each string
      results = {i: r for i, r in results if any(args[s] in r.get_prop(s, v) for v in versions)}
  
    return([i for i, r in results.items()]) # return identities

  def search_margins(self, version: str, term: str, placement: str) -> List[str]:
    return [i for i, entry in self.entries.items()
            if any(margin[0] == placement and term in margin[1] for margin in entry.margins[version])]

  def tablefy(self):
    # id, head, no. words, category, amount of each tag, margins
    # include figure margins?
    df = pd.DataFrame(columns=['entry'], data=self.entries.values())
    df['identity'] = df.entry.apply(lambda x: x.identity)
    df['title'] = df.entry.apply(lambda x: x.title['tl'])
    df['length'] = df.entry.apply(lambda x: x.length['tl'])
    df['num_materials'] = df.entry.apply(lambda x: len(x.properties['material']['tl']))
    df['margins'] = df.entry.apply(lambda x: len(x.margins))
    df['del_tags'] = df.entry.apply(lambda x: len(x.del_tags))
    df = df.drop(columns=['entry'])
    return df

# manuscript = BnF()
# print(manuscript.entry('162r_1').text('tl'))
# print(manuscript.search_margins('tl', 'gold', 'left-middle'))
