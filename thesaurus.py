""" Data transform to generate a folder of .csv files containing correction lists. """
# Python Modules
import os
import re
from typing import Dict

# Third-Party Modules
import inflection
import pandas as pd
import spacy
from tqdm import tqdm


# Local Modules
from digital_manuscript import BnF
nlp = spacy.load('en_core_web_sm')

properties = ['animal', 'body_part', 'currency', 'definition', 'environment', 'material',
              'medical', 'measurement', 'music', 'plant', 'place', 'personal_name',
              'profession', 'sensory', 'tool', 'time', 'weapon']

def get_prop_dfs(manuscript: BnF, prop_type: str) -> (pd.DataFrame, pd.DataFrame):
  """
  For each element of the 'properties' list, iterate through the manuscript, and pull out all properties of that type.
  If the property is a single word, it is simple. Multiple-word properties are complex. Put each property in the
  appropriate dictionary while counting occurrences. 

  Inputs:
    manuscript: BnF -- The BnF data used to source the terms for the thesaurus.
    prop_type: str -- one element of the list 'properties', defined globally.
  Output:
    simple_df, complex_df -- a tuple of two DataFrame: one of one word terms, and one of two word terms.
  """
  simple_properties, complex_properties = {}, {} # initalize variables
  simple_df = pd.DataFrame(columns=['freq', 'verbatim_term'])
  complex_df = pd.DataFrame(columns=['freq', 'verbatim_term'])

  for identity, entry in manuscript.entries.items():
    prop_list = entry.get_prop(prop_type, 'tl')
    for prop in prop_list: # bucket each property for each entry

      # prop = re.sub(r"’|'", '', prop)

      if prop.count(' ') == 0: # if the term is one word
        if prop in simple_properties.keys(): # if we've seen it before,
          simple_properties[prop] += 1 # increment the count
        else: # if it's new, initialize the count to one
          simple_properties[prop] = 1

      else: # if the term is multiple words, following logic above
        if prop in complex_properties.keys(): 
          complex_properties[prop] += 1
        else:
          complex_properties[prop] = 1
  
  # format the dict into a DataFrame
  for i, prop in enumerate(simple_properties.keys()):
    simple_df.loc[i] = [simple_properties[prop], prop]
  for i, prop in enumerate(complex_properties.keys()):
    complex_df.loc[i] = [complex_properties[prop], prop]

  return simple_df, complex_df

def simplify_terms(simple_df: pd.DataFrame, complex_df:pd.DataFrame) -> pd.DataFrame:
  """
  Find the semantic head of each complex term. If the head is a simple term, the head becomes the preferred label.
  
  Inputs:
    simple_df: BnF -- DataFrame containing one-word terms
    complex_df: BnF -- DataFrame containing multi-word terms
  Output:
    complex_df: BnF -- complex_df with semantic head as preferred label.
  """
  simple_terms = list(simple_df['verbatim_term'])
  for i, row in complex_df.iterrows():
    parse = nlp(row.verbatim_term)
    head = [token for token in parse if token.head.text == token.text][0].text
    if head in simple_terms:
      complex_df.loc[i, 'prefLabel_en'] = head
  return complex_df


m_k_data_to_thesaurus = f'{os.getcwd()}/manuscript-object/thesaurus'

def create_thesaurus():
  """ 
  Creates directory 'thesaurus' containing a .csv file for each property. Each .csv has three columns, count,
  verbatim_term, and prefLabel_en. Count is the number of occurrences of the verbatim term in the manuscript.
  verbatim_term is an term of the given property. prefLabel_en is the normalized form of the term.

  Normalization entails the following steps:
  1. Remove white space, punctuation, or other undesired marks
  2. Lowercase all terms
  3. Singularize all terms
  4. If the term consists of multiple words, find its semantic head. If the head is also a term of the same property,
  the preferred label becomes the semantic head.
  """
  manuscript = BnF(apply_corrections=False)

  # Create directory 'thesaurus' if one does not exist
  if not os.path.exists(m_k_data_to_thesaurus):
    os.mkdir(m_k_data_to_thesaurus)

  for prop in tqdm(properties):
    simple_df, complex_df = get_prop_dfs(manuscript, prop) # get dataframe of count, verbatim terms

    # create the prefLabel_en column by lemmatizing terms to lower case, singular, and stripped of white space
    simple_df['prefLabel_en'] = simple_df.verbatim_term.apply(lambda x: inflection.singularize(re.sub(r"’|'", '', x)).lower().strip())
    complex_df['prefLabel_en'] = complex_df.verbatim_term.apply(lambda x: inflection.singularize(x.replace('\'', '')).lower().strip())

    complex_df = simplify_terms(simple_df, complex_df) # reduce complex terms to their semantic heads
    complex_df['prefLabel_en'] = complex_df.prefLabel_en.apply(lambda x: inflection.singularize(x))

    df = pd.concat([simple_df, complex_df]) # merge dataframes 
    df.to_csv(f'{m_k_data_to_thesaurus}/{prop}.csv', index=False) # write dataframe to a file
    
create_thesaurus()
