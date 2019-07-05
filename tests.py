import os
from digital_manuscript import BnF

manuscript = BnF()
versions = ['tc', 'tcn', 'tl']

def test_balanced():
  for entry in manuscript.entries:
    assert all(entry.balanced[v] for v in versions)
  
def test_named():
  count = 0
  for entry in manuscript.entries:
    if not entry.identity:
      count += 1
  print(f'There are {count} unnamed entries')

def test_attributes():
  for entry in manuscript.entries:
    for attribute in entry.attributes:
      tc_len = len(entry.attributes[attribute]['tc'])
      tcn_len = len(entry.attributes[attribute]['tcn'])
      tl_len = len(entry.attributes[attribute]['tl'])
      if tcn_len != tc_len:
        print(f'There are unbalanced {attribute}s in {entry.identity}  versions tc and tcn')
      if tc_len != tl_len:
        print(f'There are unbalanced {attribute}s in {entry.identity}  versions tc and tl')
      if tcn_len != tl_len:
        print(f'There are unbalanced {attribute}s in {entry.identity} versions tcn and tl')

def test_matched():
  for entry in manuscript.entries:
    for version, text in entry.versions.items():
      if not text:
          print(f'There is no {version} version in {entry.identity}')

test_matched()