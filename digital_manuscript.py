import os
import pandas as pd
from typing import List, Union, Optional
from recipe import Recipe
from manuscript_helpers import generate_complete_manuscript, common_element

properties = ['animal', 'body_part', 'currency', 'definition', 'environment', 'material', 'medical', 'measurement',
              'music', 'plant', 'place', 'personal_name', 'profession', 'sensory', 'tool', 'time', 'weapon']

class Manuscript():

  def __init__(self, manuscript_data_path, entry_list: List[str] = [], load_json: bool = False, use_thesaurus: bool = True, silent: bool = False) -> None:
    """
    Initialize entire manuscript as a dictionary of Recipe objected keyed by div ID.
    If a list of IDs is given, return a dict with these entries only.
    
    Inputs:
      entry_list: A list of div IDs
      use_thesaurus: A bool deciding whether or not to apply the changes detailed in teh thesaurus.
                         For more information, checkout thesaurus.py.
    
    Outputs:
      None
    """
    complete_manuscript = generate_complete_manuscript(manuscript_data_path, load_json=load_json, use_thesaurus=use_thesaurus, silent=silent)
    if entry_list: # choose specified entries
      self.entries = {i:e for i, e in complete_manuscript.items() if e.identity in entry_list}
    else: # otherwise, return all entries
      self.entries = complete_manuscript

  def entry(self, identity: str = ''):
    """ Return entry with the given identity. """
    return self.entries.get(identity)

  search_type = Optional[Union[List[str], bool]]
  def search(self, animal: search_type = None, body_part: search_type = None, currency: search_type = None,
             definition: search_type = None, environment: search_type = None, material: search_type = None,
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
    search_strings = [k for k, v in args.items() if isinstance(v, list)] # select string element categories

    for prop in search_bools: # filter by each bool
      results = {i: r for i, r in results.items() if any(r.get_prop(prop, v) for v in versions)}
      
    
    temp = {}
    for prop in search_strings: # filter by each string
      #results = {i: recipe for i, recipe in results.items() if all(all(term in recipe.get_prop(prop, version) for term in args[prop]) for version in versions)}
      # This is 4 loops, so we're not going to try to be fancy and do it in one line.
      for version in versions:
        for i, recipe in results.items():
          if all(term in recipe.get_prop(prop, version) for term in args[prop]):
            temp[i] = recipe
            
    results = temp          

    return list(results.keys()) # return identities

  def search_margins(self, version: str, term: str, position: str = '') -> List[str]:
    results = []
    
    for identity, entry in self.entries.items():
      margin_list = entry.margins[version]
      for margin in margin_list:
        if (not position or position == margin.position) and term.lower() in margin.text.lower():
          results.append(identity)

    return sorted(list(set(results)))

  def tablefy(self):
    df = pd.DataFrame(columns=['entry'], data=self.entries.values())
    df['folio'] = df.entry.apply(lambda x: x.folio)
    df['folio_display'] = df.entry.apply(lambda x: x.folio.lstrip('0'))
    df['div_id'] = df.entry.apply(lambda x: x.identity)
    df['categories'] = df.entry.apply(lambda x: (';'.join(x.categories)))
    df['heading_tc'] = df.entry.apply(lambda x: x.title['tc'])
    df['heading_tcn'] = df.entry.apply(lambda x: x.title['tcn'])
    df['heading_tl'] = df.entry.apply(lambda x: x.title['tl'])
    for prop in properties:
      df[prop] = df.entry.apply(lambda x: '; '.join(x.get_prop(prop=prop, version='tc')))
    return df
