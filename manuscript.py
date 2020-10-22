from typing import List, Tuple, Dict
from lxml import etree as et
from pandas import DataFrame
import os
from copy import deepcopy

import utils
from entry import Entry, generate_etree, to_xml_string

def extract_folio(filepath: str) -> str:
    # get the folio out of a filepath
    return os.path.basename(filepath).split("_")[1][1:] # .../tl_p162v_preTEI.xml -> 162v

def separate_by_id(filepath: str) -> Dict[str, et.Element]:
    # takes a file path, reads it as XML, and processes it into separate elements by id
    folio = extract_folio(filepath)
    entries = {}

    print(f"Separating divs in file: {filepath}")
    xml = et.parse(filepath)

    divs = xml.findall("div") # not recursive; there should be no nested divs

    for div in divs:
        identity = div.get("id")
        key = identity if identity else "" # there must be a better way to do this; seems monadic?

        if key in entries.keys():
            entries[key].append(div) # add continued entry in-place
        else:
            root = et.Element("entry") # start a new entry with an <entry></entry> element
            root.append(div) # put the current div in the new tree
            entries[key] = root

    # note this will result in overwriting for id-less divs, but my understanding is that those divs should be ignored anyway
    print(f"Found {len(entries)} div{'' if len(entries)==1 else 's'} in file {filepath}")

    return entries

def generate_manuscript(directory) -> Dict[str, Entry]:
    # directory: file path to a directory of data files
    print(f"Generating entries from files in folder {directory}")

    xml_dict: Dict[Tuple(str, str), et.Element] = {}

    for root, _, files in os.walk(directory):
        for filename in files:
            folio = extract_folio(filename)
#            if extract_folio(filename) in folios: # for specifying folios
            entries = separate_by_id(os.path.join(root, filename))

            for identity, xml in entries.items():
                if identity in xml_dict.keys():
                    for div in xml.findall("div"): # extract divs from xml
                        xml_dict[identity].append(div) # append each div
                elif identity: # only add it to the dict if it has an identity
                    xml_dict[identity] = xml

    entries_dict = {}
    # now convert each value of entries_dict into its appropriate Entry object
    for identity, xml in xml_dict.items():
        print(f"Generating entry with folio {folio}, ID {identity}")
        entries_dict[identity] = Entry(xml, folio=folio, identity=identity)

    print(f"Generated {len(entries)} entr{'y' if len(entries)==1 else 'ies'}.")
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

        # does having 3x as many Entry objects waste some space by duplicating secondary information? yes. is it a good idea anyway? yes!
        print(f"Generating Manuscript object from {directory}")
        self.entries = {}
        for version in utils.versions:
            self.entries[version] = generate_manuscript(os.path.join(directory, version))

        # TODO: give less confusing names to these two instance variables
        self.directory = directory
        self.data_path = os.path.dirname(directory) # one up from given data directory

    # TODO: write a search method

    def update(self):
        self.update_metadata()
        self.update_ms_txt()
        self.update_entries()
        self.update_all_folios()

    def update_ms_txt(self):
        """
        Update /m-k-manuscript-data/update_ms/ with the current manuscript from /ms-xml/.
        Iterate through /ms-xml/ for each version, remove tags, and save to /ms-txt/.
        """
        for version, folios_dict in self.generate_ms_txt():
            for filename, folio in folios:
                outfile = os.path.join(self.data_path, "ms-txt", version, filename.replace("xml", "txt"))
                with open(outfile, 'w') as fp:
                    print(f"Writing folio {folio} to {outfile}")
                    fp.write(folio.text)

    def generate_ms_txt(self):
        versions = {}
        for version in utils.versions:
            folios_dict = {}
            for root, _, files in os.walk(os.path.join(self.directory, version)):
                for filename in files:
                    # I'm making this simple at the sacrifice of a tiny bit of speed
                    # Forgive me
                    # TODO: make entry.py do this with a module function called from the classmethod so there's one universal place to generate an Entry etree from a file (we already have one for from a string: generate_etree()!)
                    print(f"Generating entry from file {os.path.join(root, filename)}")
                    folios_dict[filename] = Entry.from_file(os.path.join(root, filename))
        return versions

    def update_entries(self):
        """
        Update /m-k-manuscript-data/entries/ with the current manuscript from /ms-xml/.
        """

        txt_dir = os.path.join(self.data_path, "entries", "txt")
        xml_dir = os.path.join(self.data_path, "entries", "xml")

        for version in utils.versions:
            txt_path = os.path.join(txt_dir, version)
            xml_path = os.path.join(xml_dir, version)
            os.makedirs(txt_path, exist_ok=True)
            os.makedirs(xml_path, exist_ok=True)

            for identity, entry in self.entries[version].items():
                filepath_txt = os.path.join(txt_path, f'{version}_{entry.identity}.txt')
                filepath_xml = os.path.join(xml_path, f'{version}_{entry.identity}.xml')

                content_txt = entry.text
                content_xml = entry.xml_string # should already have an <entry> root tag :)

                with open(filepath_txt, 'w', encoding='utf-8') as fp:
                    print(f"Writing entry {entry.identity} txt to {filepath_txt}")
                    fp.write(content_txt)

                with open(filepath_xml, 'w', encoding='utf-8') as fp:
                    print(f"Writing entry {entry.identity} XML to {filepath_xml}")
                    fp.write(content_xml)

    def update_all_folios(self):
        """
        Update /m-k-manuscript-data/allFolios/ with the current manuscript from /ms-xml/.
        """
        txt_dir = os.path.join(self.data_path, "allFolios", "txt")
        xml_dir = os.path.join(self.data_path, "allFolios", "xml")

        for version in utils.versions:
            content_txt = self.generate_all_folios(method="txt", version=version)
            content_xml = self.generate_all_folios(method="xml", version=version)

            txt_path = os.path.join(txt_dir, version)
            xml_path = os.path.join(xml_dir, version)
            os.makedirs(txt_path, exist_ok=True)
            os.makedirs(xml_path, exist_ok=True)

            filepath_txt = os.path.join(txt_path, f"all_{version}.txt")
            filepath_xml = os.path.join(xml_path, f"all_{version}.xml")

            with open(filepath_txt, 'w', encoding='utf-8') as fp:
                print(f"Writing allFolios txt version {version} to {filepath_txt}")
                fp.write(content_txt)

            with open(filepath_xml, 'w', encoding='utf-8') as fp:
                print(f"Writing allFolios XML version {version} to {filepath_txt}")
                fp.write(content_xml)

    def generate_all_folios(self, method="txt", version="tl"):
        # method: "txt" or "xml"
        # version: "tc", "tcn", or "tl"

        if method=="txt":
            content = "" # string representing the entire text version
            for identity, entry in self.entries[version].items():
                print(f"Adding entry {identity} to allFolios version {version} {method}")
                content += entry.text #TODO: add line breaks between entries?

        elif method=="xml":
            root = et.Element("all") # root element to wrap the entire xml string
            for identity, entry in self.entries[version].items():
                print(f"Adding entry {identity} to allFolios version {version} {method}")
                divs = [deepcopy(div) for div in list(entry.xml)] # avoid modifying instance variables
                root.extend(divs) # add children of <entry> element
            content = to_xml_string(root)

        else:
            raise Exception(f"Invalid method: '{method}'. Methods: txt, xml")

        return content

    def update_metadata(self):
        df = self.generate_metadata()
        df.drop(columns=utils.versions, inplace=True) # this is just memory addresses
        outfile = os.path.join(self.data_path, "metadata", "entry_metadata.csv")
        print(f"Writing metadata to {outfile}")
        df.to_csv(outfile, index=False)

    def generate_metadata(self):
        """
        Update /m-k-manuscript-data/metadata/entry_metadata.csv with the current manuscript. Create a Pandas DataFrame
        indexed by entry. Create data columns, and remove the column that contains the entry objects. Save File.
        """
        print("Generating metadata")
        # for making entry-metadata.csv
        # use tl version for basic info
        # TODO: this is almost identical to Matthew's code; can be we improve on it at all?
        df = DataFrame(columns=utils.versions, data=self.entries)
        df['folio'] = df.tl.apply(lambda x: x.folio)
        df['folio_display'] = df.folio.apply(lambda x: x.lstrip('0')) # remove leading zeros
        df['div_id'] = df.tl.apply(lambda x: x.identity)
        df['categories'] = df.tl.apply(lambda x: (';'.join(x.categories)))
        for version in utils.versions:
            df[f'heading_{version}'] = df[version].apply(lambda x: x.title)
        for prop, tag in utils.prop_dict.items():
            for version in utils.versions:
                df[f'{tag}_{version}'] = df[version].apply(lambda x: ';'.join(x.properties[prop]))

        return df
