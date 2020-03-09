import re
import pandas as pd
from digital_manuscript import BnF


def find_percent_marginal(entry, version):
    if len(entry.margins) == 0:
        return 0
    
    margin_sum = 0
    for margin in entry.margins[version]:
        margin_sum += margin.length
    
    return 100 * margin_sum / entry.length[version]

def find_percent_continued(entry, version):
    continued_sum = 0
    parts = re.findall(r'(<div([\w\s=";-]*)>(.*?)</div>)', re.sub(r'\s+', ' ', entry.text(version, True)))
    for part in parts:
        _, attributes, text = part
        if 'continues="yes"' in attributes:
                text = re.sub(r'<.*?>', '', text)
                continued_sum += len(text)
    return 100 * continued_sum / entry.length[version]

def analyze():
  manuscript = BnF()
  df = pd.DataFrame(columns=['entry_id', 'length_tc', 'length_tcn', 'length_tl',
                           'percent_marginal_tc', 'percent_marginal_tcn', 'percent_marginal_tl',
                           'percent_continued_tc', 'percent_continued_tcn', 'percent_continued_tl'])
  versions = ['tc', 'tcn', 'tl']
  i=0

  for identity, entry in manuscript.entries.items():
      if len(entry.margins) > 0 or 'continues="yes"' in entry.text('tl', xml=True):
          percent_marginal, percent_continued = {}, {}
          for version in versions: # populate dicts
              percent_marginal[version] = find_percent_marginal(entry, version)
              percent_continued[version] = find_percent_continued(entry, version)
          
          # add to DataFrame
          df.loc[i] = [entry.identity, entry.length['tc'], entry.length['tcn'], entry.length['tl'],
                      percent_marginal['tc'], percent_marginal['tcn'], percent_marginal['tl'],
                      percent_continued['tc'], percent_continued['tcn'], percent_continued['tl']]
          i += 1 # increment row count
  
  df.to_csv('distribution_analysis.csv', index=False)

analyze()
