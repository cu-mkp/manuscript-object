# Last Updated | 2020-09-14
# Python Modules
import os
import sys
import re
from typing import List, Dict
import json
import argparse

# Third Party Modules
import pandas as pd
from datetime import datetime

# Local Modules
from digital_manuscript import BnF
from recipe import Recipe

versions = ['tc', 'tcn', 'tl']
properties = ['animal', 'body_part', 'currency', 'definition', 'environment', 'material', 'medical', 'measurement',
              'music', 'plant', 'place', 'personal_name', 'profession', 'sensory', 'tool', 'time', 'weapon',
              'german', 'greek', 'italian', 'latin', 'occitan', 'poitevin']
prop_dict = {'animal': 'al', 'body_part': 'bp', 'currency': 'cn', 'definition': 'df',
              'environment': 'env', 'material': 'm', 'medical': 'md', 'measurement': 'ms',
              'music': 'mu', 'plant': 'pa', 'place': 'pl', 'personal_name': 'pn',
              'profession': 'pro', 'sensory': 'sn', 'tool': 'tl', 'time': 'tmp', 'weapon': 'wp',
              'german': 'de', 'greek': 'el', 'italian': 'it', 'latin': 'la', 'occitan': 'oc', 'poitevin': 'po',}

manuscript_data_path = os.path.dirname(os.getcwd()) + "/m-k-manuscript-data" # default

def update_metadata(manuscript: BnF, manuscript_data_path: str) -> None:
  """
  Update /m-k-manuscript-data/metadata/entry_metadata.csv with the current manuscript. Create a Pandas DataFrame
  indexed by entry. Create data columns, and remove the column that contains the entry objects. Save File.

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """
  # create DataFrame (spreadsheet) with one entry per row
  df = pd.DataFrame(columns=['entry'], data=manuscript.entries.values())
  df['folio'] = df.entry.apply(lambda x: x.folio)
  df['folio_display'] = df.entry.apply(lambda x: x.folio.lstrip('0'))
  df['div_id'] = df.entry.apply(lambda x: x.identity)
  df['categories'] = df.entry.apply(lambda x: (';'.join(x.categories)))
  df['heading_tc'] = df.entry.apply(lambda x: x.find_title(x.versions['tc'], remove_del_text=True))
  df['heading_tcn'] = df.entry.apply(lambda x: x.find_title(x.versions['tcn'], remove_del_text=True))
  df['heading_tl'] = df.entry.apply(lambda x: x.find_title(x.versions['tl'], remove_del_text=True))

  for prop, tag in prop_dict.items():
    for version in versions:
      df[f'{tag}_{version}'] = df.entry.apply(lambda x: '; '.join(x.get_prop(prop=prop, version=version)))
      
  # remove entry column, since it only displays memory address
  df.drop(columns=['entry'], inplace=True)

  df.to_csv(f'{manuscript_data_path}/metadata/entry_metadata.csv', index=False)

def update_entries(manuscript: BnF, manuscript_data_path: str) -> None:
  """
  Update /m-k-manuscript-data/entries/ with the current manuscript from /ms-xml/. For each version, delete all existing
  entries. Regenerate folio text entry by entry, and save the file.

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """

  for path in [f'{manuscript_data_path}/entries', f'{manuscript_data_path}/entries/txt', f'{manuscript_data_path}/entries/xml']:
    if not os.path.exists(path):
      os.mkdir(path)

  for version in versions:
    txt_path = f'{manuscript_data_path}/entries/txt/{version}'
    xml_path = f'{manuscript_data_path}/entries/xml/{version}'

    # If the entries/txt or xml directory does not exist, create it. Otherwise, clear the directory.
    for path in [txt_path, xml_path]:
      if not os.path.exists(path):
        os.mkdir(path)
      elif len(os.listdir(path)) > 0: # remove existing files
        for f in os.listdir(path):
          os.remove(os.path.join(path, f))

    # Write new files with manuscript object
    for identity, entry in manuscript.entries.items():
      if identity: # TODO: resolve issue of unidentified entries
        # TODO: ask for a naming convention
        filename_txt = f'{txt_path}/{version}_{entry.identity}.txt'
        filename_xml = f'{xml_path}/{version}_{entry.identity}.xml'

        content_txt = entry.text(version, xml=False)
        content_xml = "<entry>" + entry.text(version, xml=True) + "</entry>"

        f_txt = open(filename_txt, 'w')
        print(f"Writing entry to /entries/txt/{version}/{os.path.basename(filename_txt)}...")
        f_txt.write(content_txt)
        f_txt.close()

        f_xml = open(filename_xml, 'w')
        print(f"Writing entry to /entries/xml/{version}/{os.path.basename(filename_xml)}...")
        f_xml.write(content_xml)
        f_xml.close()

def update_all_folios(manuscript: BnF, manuscript_data_path: str) -> None:
  """
  Update /m-k-manuscript-data/allFolios/ with the current manuscript from /ms-xml/.

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """
  for b in [True, False]: # xml and txt respectively
    for version in versions:
      text = ''
      folder = 'xml' if b else 'txt'

      # add text entry by entry, with two line breaks in between each
      for identity, entry in manuscript.entries.items():
        new_text = entry.text(version, xml=b)
        text = f'{text}\n\n{new_text}' if text else new_text

      if b:
        text = "<all>" + text + "</all>"

      # write file
      f = open(f'{manuscript_data_path}/allFolios/{folder}/all_{version}.{folder}', 'w')
      print(f"Writing to /allFolios/{folder}/all_{version}.{folder}...")
      f.write(text)
      f.close()

def update_ms(manuscript: BnF, manuscript_data_path: str) -> None:
  """
  Update /m-k-manuscript-data/update_ms/ with the current manuscript from /ms-xml/.
  Iterate through /ms-xml/ for each version, remove tags, and save to /ms-txt/.

  Input:
    manuscript -- Python object of the manuscript defined in digital_manuscript.py
  Output:
    None
  """
  for version in versions:
    for r, d, f in os.walk(f'{manuscript_data_path}/ms-xml/{version}'):
      for filename in f: # iterate through /ms-xml/{version} folder
        # read xml file
        text = ''
        filepath = f'{manuscript_data_path}/ms-xml/{version}/{filename}'
        with open(filepath, encoding="utf-8", errors="surrogateescape") as f:
          text = f.read()

        # remove xml, normalize whitespace
        text = text.replace('\n', '**NEWLINE**')
        text = re.sub(r'<.*?>', '', text)
        text = text.replace('**NEWLINE**', '\n')
        text = text.strip(' \n')

        # write txt file
        txt_filepath = filepath.replace('xml', 'txt')
        f = open(txt_filepath, 'w')
        print(f"Writing entry to /ms-txt/{version}/{os.path.basename(txt_filepath)}")
        f.write(text)
        f.close()

def update_time():
  """ Extract timestamp at the top of this file and update it. """
  # Initialize date to write and container for the text
  now_str = str(datetime.now()).split(' ')[0]
  lines = []

  # open file, extract text, and modify
  with open('./update.py', 'r') as f:
    lines = f.read().split('\n')
    lines[0] = f'# Last Updated | {now_str}'

  # write modified text
  f = open('./update.py', 'w')
  f.write('\n'.join(lines))
  f.close

def make_json(manuscript: BnF):
  '''
  Make the manuscript into a JSON-friendly dictionary with the following format:
    {
      "entries" : {
        "127v_2" : {
          "id" : "127v_2",
          "folio" : "127v",
          "versions" : {
            "tc" : THE_ENTIRE_RAW_TC_XML,
            "tcn" : THE_ENTIRE_RAW_TCN_XML,
            "tl" : THE_ENTIRE_RAW_TL_XML
          },
          "title" : {
            "tc" : TC_TITLE,
            "tcn" : TCN_TITLE,
            "tl" : TL_TITLE,
          },
          "categories" : [
            CATEGORY_1,
            CATEGORY_2,
            ...
          ],
          "length" : {
            "tc" : LENGTH_TC,
            "tcn" : LENGTH_TCN,
            "tl" : LENGTH_TL
          },
          "properties" : {
            "animal" : {
              "tc" : [TERM_1, %TERM_2, ...],
              "tcn" : [TERM_1, %TERM_2, ...],
              "tl" : [TERM_1, %TERM_2, ...]
            },
            ... more properties
          }
          // pretty sure we're gonna skip margins, del_tags, and captions
          // and we can just recompute those from XML upon loading JSON
        },
        "127v_3" : {
          ...
        },
        ... more entries
      }
    }
  '''
  manuscript_dict = {}
  manuscript_dict["entries"] = {}
  for identity, entry in manuscript.entries.items():
    manuscript_dict["entries"][identity] = {
      "id" : entry.identity,
      "folio" : entry.folio,
      "versions" : entry.versions,
      "title" : entry.title,
      "categories" : entry.categories,
      "length" : entry.length,
      "properties" : entry.properties,
    }
  return manuscript_dict

def save_as_json(manuscript: BnF, outfile) -> None:
  '''
  Save the manuscript in JSON format to a specified .json file.
  '''
  manuscript_dict = make_json(manuscript)
  f = open(outfile, mode="w")
  json.dump(manuscript_dict, f, indent=4)
  f.close()

def update():

  parser = argparse.ArgumentParser(description="Generate derivative files from original ms-xml folios.")
  parser.add_argument('-d', '--dry-run', help="Generate as usual, but do not write derivatives.", action="store_true")
  parser.add_argument('-s', '--silent', help="Silence output. Do not write generation progress to terminal.", action="store_true")
  parser.add_argument('-b', '--bypass', help="Bypass user y/n confirmation. Useful for automation.", action="store_true")
  parser.add_argument('-c', '--cache', help="Save manuscript object to a JSON cache for quicker loading next time.", action="store_true")
  parser.add_argument('-q', '--quick', help="Use JSON cache of manuscript object to speed up generation process. Don't do this if you need to include changes from ms-xml!", action="store_true")
  parser.add_argument('-a', '--all-folios', help="Generate allFolios derivative files. Disables generation of other derivatives unless those are also specified.", action="store_true")
  parser.add_argument('-m', '--metadata', help="Generate metadata derivative files. Disables generation of other derivatives unless those are also specified.", action="store_true")
  parser.add_argument('-t', '--txt', help="Generate ms-txt derivative files. Disables generation of other derivatives unless those are also specified.", action="store_true")
  parser.add_argument('-e', '--entries', help="Generate entries derivative files. Disables generation of other derivatives unless those are also specified.", action="store_true")
  parser.add_argument("path", nargs="?", action="store", default=manuscript_data_path, help="Path to m-k-manuscript-data directory. Defaults to the sibling of your current directory.")

  options = parser.parse_args()

  # verify manuscript-data path
  assert(os.path.exists(options.path)), ("Could not find manuscript data directory: " + options.path)
  assert(os.path.exists(options.path + "/ms-xml")), ("Could not find ms-xml folder in manuscript data directory: " + options.path + "/ms-xml")

  if not options.bypass:
    okay = input(f"Using manuscript data path: {options.path}. Confirm (y/n)? ").lower() in ("y", "yes")
    if not okay:
      return

  # if no specific derivatives were specified, generate all of them
  if not [op for op in [options.all_folios, options.metadata, options.txt, options.entries] if op]:
    generate_all_derivatives = True
  else:
    generate_all_derivatives = False

  manuscript = BnF(options.path, load_json=options.quick, apply_corrections=False, silent=options.silent)

  if not options.dry_run:
    if options.metadata or generate_all_derivatives:
      print('Updating metadata')
      update_metadata(manuscript, options.path)

    if options.entries or generate_all_derivatives:
      print('Updating entries')
      update_entries(manuscript, options.path)

    if options.txt or generate_all_derivatives:
      print('Updating ms-txt')
      update_ms(manuscript, options.path)

    if options.all_folios or generate_all_derivatives:
      print('Updating allFolios')
      update_all_folios(manuscript, options.path)

    update_time()

  if options.cache:
    print("Saving to JSON")
    save_as_json(manuscript, "digital_manuscript.json")

if __name__ == "__main__":
  update()
