import os
from digital_manuscript import BnF

manuscript = BnF(apply_corrections=False)
versions = ['tc', 'tcn', 'tl']

def test_balanced():
  perfect = True
  for entry in manuscript.entries:
    if not all(entry.balanced[v] for v in versions):
      print(f'{entry.identity} is not balanced.')
      perfect = False
  if perfect:
    print('All entries are balanced')

def test_properties():
  for entry in manuscript.entries:
    for prop in entry.properties:
      tc_len = len(entry.properties[prop]['tc'])
      tcn_len = len(entry.properties[prop]['tcn'])
      tl_len = len(entry.properties[prop]['tl'])
      
      if not tc_len == tcn_len == tl_len:
        print(f'{entry.identity}, {prop} -- tc: {tc_len}, tcn: {tcn_len}, tl: {tl_len}')
        print(entry.properties[prop]['tc'])
        print(entry.properties[prop]['tcn'])
        print(entry.properties[prop]['tl'])
        print()

def test_matched():
  perfect = True
  for entry in manuscript.entries:
    for version, text in entry.versions.items():
      if not text:
        print(f'There is no {version} version in {entry.identity}')
        perfect = False
  if perfect:
    print('Each entry has each version')

# TODO: MARGINS

test_balanced()
test_properties()
test_matched()