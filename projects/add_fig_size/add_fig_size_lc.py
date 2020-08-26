""" Add figure size attribute to tags. """
# Python Modules
import re
import os

# Third-Party Modules
import pandas as pd

# Local Modules
from digital_manuscript import BnF
# TODO: make sure you can import digital manuscript.

# set constants
versions = ['tc', 'tcn', 'tl']
# TODO: Adjust path to whatetver it is on your machine
MANUSCRIPT_PATH = os.getcwd() + '/../m-k-manuscript-data'
CATEGORIES_PATH = os.getcwd()

# initialize variables
manuscript = BnF()
df = pd.read_csv(f'{CATEGORIES_PATH}/sizes.csv').fillna('')
size_dict = {} # identity: category

# store contents of categories.csv in size_dict
for i, row in df.iterrows():
  identity, XPath_Location, folio, link, size_suggestion, notes = row
  if size_suggestion:
      size_dict[identity] = size_suggestion

# read and write files
for version in versions:
  dir_path = f'{MANUSCRIPT_PATH}/ms-xml/{version}/'
  for r, d, f in os.walk(dir_path):
    for filename in f: # iterate through /ms-xml/ folder
      data = None
      with open(dir_path + filename, 'r') as f: # extract text
        data = f.readlines()

      for i, line in enumerate(data): # iterate through each line
        if '<figure ' in line: # find line of interest
          identity = re.findall(r'(id="(.*?)")', line)[0] # find indentity attribute in div tag
          size_from_xml = re.findall(r'(size="(.*?)")', line)
          size_from_csv = size_dict.get(identity[1])
          # if one is already in the manuscript, do nothing
          if not size_from_xml:
            size = size_dict.get(identity[1]) # find corresponding categories
            if size:
              data[i] = line.replace(identity[0], f'{identity[0]} size="{size}"') # replace categories with fig_size?

      # write files
      with open(dir_path + filename, 'w') as f:
        f.writelines(data)
