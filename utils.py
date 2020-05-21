# Python Modules
import os

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'
m_k_data_to_thesaurus = f'{m_path}/manuscript-object/thesaurus'

versions = ['tc', 'tcn', 'tl']
properties = ['animal', 'body_part', 'currency', 'definition',
              'environment', 'material', 'medical', 'measurement',
              'music', 'plant', 'place', 'personal_name',
              'profession', 'sensory', 'tool', 'time', 'weapon']

prop_dict = {'animal': 'al', 'body_part': 'bp', 'currency': 'cn', 'definition': 'def',
              'environment': 'env', 'material': 'm', 'medical': 'md', 'measurement': 'ms',
              'music': 'mu', 'plant': 'pa', 'place': 'pl', 'personal_name': 'pn',
              'profession': 'pro', 'sensory': 'sn', 'tool': 'tl', 'time': 'tmp', 'weapon': 'wp',
              'german': 'de', 'greek': 'ge', 'italian': 'it', 'latin': 'la', 'occitan': 'oc', 'poitevin': 'po',}