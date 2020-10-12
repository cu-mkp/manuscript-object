from typing import List, Tuple, Dict, Optional
from lxml import etree as et
import os

import utils
from entry import Entry, generate_etree

def extract_folio(filepath: str) -> str:
    # get the folio out of a filepath
    return os.path.basename(filepath).split("_")[1][1:] # .../tl_p162v_preTEI.xml -> 162v

def separate_by_id(filepath: str) -> Dict[str, et.Element]:
    # takes a file path, reads it as XML, and processes it into separate elements by id
    folio = extract_folio(filepath)
    entries = {}

    with open(filepath, "r") as fp:
        xml_string = fp.read().encode()
    xml = generate_etree(xml_string)

    divs = xml.findall("div") # not recursive; there should be no nested divs

    for div in divs:
        identity = div.get("id")
        key = identity if identity else "" # there must be a better way to do this

        if key in entries.keys():
            entries[key].append(div) # add continued entry in-place
        else:
            root = et.Element("entry") # start a new entry with an <entry></entry> element
            root.append(div) # put the current div in the new tree
            entries[key] = root

    # note this will result in overwriting for id-less divs, but my understanding is that those divs should be ignored anyway

    return entries

def generate_entries(directory) -> Dict[str, Entry]:
    print(directory)
    # directory: file path to a directory of data files
    xml_dict: Dict[Tuple(str, str), et.Element] = {}

    for root, _, files in os.walk(directory):
        for filename in files:
            folio = extract_folio(filename)
#            if extract_folio(filename) in folios: # for specifying folios
            entries = separate_by_id(os.path.join(root, filename))

            for identity, xml in entries.items():
                key = (folio, identity)
                if key in xml_dict.keys():
                    xml_dict[key].append(xml)
                elif identity: # only add it to the dict if it has an identity
                    xml_dict[key] = xml
    
    entries_dict = {}
    # now convert each value of entries_dict into its appropriate Entry object
    for (folio, identity), xml in xml_dict.items():
        entries_dict[identity] = Entry(xml, folio=folio, identity=identity)

    return entries_dict


class Manuscript():
    def __init__(self, directory):
        # directory: file path to the directory of data files organized by version
        
        #TODO: implement specifying a range of entries you want, like so:
        #entries: Union[bool, List[str]]=True
        # entries: a list or a boolean describing which entries to load
        #          True means all; False or [] means none; a list of entry IDs and/or folios only loads those
        # TODO: allow ranges of entries and folios to be specified like 007v..014r
        # TODO: allow ints
        # TODO: allow excluding leading 0s

        #ids = [el for el in entries if el[-1] not in ('r', 'v')] # e.g. "017v_2"
        #folios = [el for el in entries if el not in ids] # e.g. "017v"

        self.entries = {}
        for version in utils.versions:
            self.entries[version] = generate_entries(os.path.join(directory, version))

    # TODO: write a search method

    def derivative_ms_txt(self):
        pass

    def derivative_entries(self):
        pass

    def derivative_all_folios(self):
        pass

    def derivative_metadata(self):
        pass

    def tablefy(self):
        # for making entry-metadata.csv
        pass
