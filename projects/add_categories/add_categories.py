import pandas as pd
import re
import os
from digital_manuscript import BnF

if not os.path.exists('categories'):
    os.mkdir('categories')

manuscript = BnF()
df = pd.read_csv('categories.csv').fillna('')
identity_dict = {}

for i, row in df.iterrows():
  cat_string = ';'.join([x for x in [row.category, row.category1, row.category2] if x])
  identity_dict[row.div_id] = cat_string

for entry in manuscript.entries:
  cat_string = identity_dict.get(entry.identity, '')
  new_text = entry.versions['tl'].replace('<div', f'<div categories="{cat_string}"')

  f = open(f'categories/{entry.identity}.txt', "w")
  f.write(new_text)
  f.close()
