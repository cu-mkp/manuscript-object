import re
from typing import List, Dict, Optional
from collections import OrderedDict
from margin import Margin
from lxml import etree as et

re_tags = re.compile(r'<.*?>') # selects any tag
re_head = re.compile(r'<head( (margin|comment)="[\w-]*")?>(.*?)</head>')
re_materials = re.compile(r'<m>(.*?)<\/m>') # selects text between materials tags
prop_dict = {'animal': 'al', 'body_part': 'bp', 'currency': 'cn', 'definition': 'df', 'deleted': 'del',
              'environment': 'env', 'material': 'm', 'medical': 'md', 'measurement': 'ms',
              'music': 'mu', 'plant': 'pa', 'place': 'pl', 'personal_name': 'pn',
              'profession': 'pro', 'sensory': 'sn', 'tool': 'tl', 'time': 'tmp', 'weapon': 'wp',
              'german': 'de', 'greek': 'el', 'italian': 'it', 'latin': 'la', 'occitan': 'oc', 'poitevin': 'po'}

prop_dict_reverse = {v: k for k, v in prop_dict.items()}

class Recipe:

    def __init__(self, identity: str, folio: str, tc: str, tcn: str, tl: str, json_dict = None) -> None:
        
        if json_dict:
            self.identity = json_dict["id"] # id of the entry
            self.folio = json_dict["folio"] # folio of the entry
            self.versions = json_dict["versions"] # dict that contains xml text
            self.title = json_dict["title"]
            self.categories = json_dict["categories"]
            self.length = json_dict["length"]

            self.properties: Dict[str, Dict[str, List[str]]] # {prop_type: {version: [prop1, prop2, ...]}}
            self.properties = json_dict["properties"]

        else:
            self.identity: str = identity # id of the entry
            self.folio: str = folio # folio of the entry
            self.versions: Dict[str, str] = {'tc': tc, 'tcn': tcn, 'tl': tl} # dict that contains xml text
            self.title = {k: self.find_title(v) for k, v in self.versions.items()}
            self.categories: List[str] = self.find_categories(self.text('tl', xml=True))
            self.length = {k: self.clean_length(v) for k, v in self.versions.items()}

            self.properties: Dict[str, Dict[str, List[str]]] # {prop_type: {version: [prop1, prop2, ...]}}
            self.properties = self.find_all_properties()

        self.margins = self.find_margins()
        self.del_tags = self.find_del()
        self.captions = {k: self.find_captions(k) for k in self.versions.keys()}

    def find_categories(self, text: str) -> List[str]:
        """
        Use a regex to find categories tagged in the div tag. Since categories are the same for each version,
        the 'tl' version is used.

        Inputs:
          text: str -- the tl version of the manuscript with xml tags
        Output:
          List[str] -- A list of the categories
        """
        text = re.sub(r'\s+', ' ', text)
        categories = re.search(r'categories="[\w\s;]*"', text)
        if categories:
            return categories[0].split('"')[1].split(';')
        return []

    def find_title(self, text: str, remove_del_text=False) -> str:
        """ 
        Use a regex to find text in between head tags. Specifying the version is not necessary since it is
        included in the dict comprehension statement where this function is called.

        Inputs:
          text: str -- the text of the entry with xml tags
        Output:
          str -- title text
        """
        text = text.replace('<sup>', '[').replace('</sup>', ']') # mark editor supplied titles with square brackets
        text = re.sub(r'\s+', ' ', text.replace('\n', ' '))

        titles = re_head.search(text)
        if remove_del_text:
            return '' if not titles else re.sub(r'\s+', ' ', re_tags.sub('', re.sub(r'<del>.*</del>', '', titles[0])))
        else:
            return '' if not titles else re_tags.sub('', titles[0])

    def clean_length(self, text: str) -> int:
        # TODO: make it word count instead of character count.
        text = re_tags.sub('', text)
        text = re.sub(r'\s+', ' ', text)
        return len(text)

    def find_tagged_text(self, text: str, tag: str) -> List[str]:
        """
        Use lxml parsing to find text between the given tag from the source text. This is a helper function for
        find_all_properties, which handles specifying the version.
        
        Input:
          text: str -- source text with xml tags
          tag: str -- property tag of the manuscript listed above in prop_dict
        Output:
          List[str]: A list of the form [tagged_str1, tagged_str2, ...]
        """

        text = "<entry>" + text + "</entry>" # this is temporary band-aid code to stave off a larger problem.
                                             # see: https://github.com/cu-mkp/manuscript-object/issues/33.

        root = et.XML(text.encode()) # lxml only accepts encoded bytes versions of strings
        tags = root.findall(".//" + tag) # ".//" is an XPath prefix that searches the entire XML document recursively (not just at current level)
        return [et.tostring(tag, method="text", encoding="utf-8", with_tail=False).decode().replace("\n", " ") for tag in tags]

    def find_all_properties(self):
        """
        Create the properties dict. For each property type, create a dictionary keyed by version
        with find_tagged_text(), defined above. Add this dictionary to another dictionary keyed
        by property type.

        Inputs:
          None
        Output:
          Dict[str, Dict[str, List[str]]] -- see structure below

          {
            prop_type1: {
                'tc': [tc_prop_0, tc_prop_1, ...],
                'tcn': [tcn_prop_0, tcn_prop_1, ...],
                'tl': [tl_prop_0, tl_prop_1, ...]
            }, 
            prop_type_2: {
                ...
            }, 
            ...
          }
        """
        all_properties = {}
        for prop, tag in prop_dict.items():
            p_dict = {}
            for version in self.versions:
                text = self.text(version, xml=True)
                p_dict[version] = self.find_tagged_text(text, tag)
            all_properties[prop] = p_dict
        return all_properties

    def get_prop(self, prop, version='tl'):
        """ Getter method for prop based on version. Version defaults to 'tl'."""
        return self.properties[prop][version]

    def find_margins(self) -> Dict[str, List[Margin]]:
        """
        Use regex to search for margins and identify position and render. Initialize a new instance of
        the margin class with this information. Save these margins in lists keyed by version in a dictionary.

        Inputs:
          None
        Outputs:
          Dict[str, List[Margin]] -- See structure below
          {
              'tc': [Margin0, Margin1, ...],
              'tcn': [Margin0, Margin1, ...],
              ...
          }
        """

        margins = {}
        for version in self.versions.keys():
            margin_list = []
            text = re.sub(r'\s+', ' ', self.text(version, xml=True))
            search = re.findall(r'<ab margin="([\w-]*)"( render="([\w-]*)")?>(.*?)<\/ab>', text)
            for tup in search:
                position, _, render, margin_text = tup
                margin_list.append(Margin(self.identity, position, margin_text, render))
            margins[version] = margin_list
        return margins

    def find_del(self) -> List[str]:
        d = re.findall(r'<del>(.*?)</del>', self.versions['tl'])
        return d if d else []

    def find_captions(self, version: str) -> List[str]:
        c = re.findall(r'<caption>(.*?)</caption>', self.versions[version])
        return c if c else []

    def get_title(self, version: str = 'tl'):
        return self.title[version]
        
    def get_head(self, text: str) -> str:
        """ search text for text in a <head> tag. """
        text = text.replace('<sup>', '[') # mark editor supplied titles with square brackets
        text = text.replace('</sup>', ']')

        head = re_head.search(text)
        if head:
            return re_tags.sub('', head[0])
        return ''

    def get_identity(self) -> str:
        """ Getter method for identity. """
        return self.identity

    def text(self, version: str, xml: bool = False) -> str:
        """ Getter method for text based on version, xml. """
        if xml:
            return self.versions[version]

        text = "<entry>" + self.versions[version] + "</entry>" # this is temporary band-aid code to stave off a larger problem.
                                                               # see: https://github.com/cu-mkp/manuscript-object/issues/33.
        root = et.XML(text.encode()) # lxml only accepts encoded bytes versions of strings
        return et.tostring(root, method="text", encoding="utf-8").decode()

    def context(self, term: str, version: str) -> str:
        """ Returns five words on either side of the given term in the specified version. """
        text = self.text(version).lower()
        if term in text:
            #TODO: clean up this regex
            context = re.search(fr'((\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?{term}(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?)', text)
            if context:
                return context[0]
        return f'{term} not found in {version} {self.identity}'

