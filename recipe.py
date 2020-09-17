from typing import List, Dict, Optional
from collections import OrderedDict
from margin import Margin
from lxml import etree as et

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
            self.xml = json_dict["xml"] # dict that contains xml strings keyed by version
            self.root = {k: self.make_etree(v) for k, v in self.xml.items()}
            self.txt = json_dict["txt"] # dict that contains txt strings keyed by version
            self.title = json_dict["title"]
            self.categories = json_dict["categories"]
            self.length = json_dict["length"]

            self.properties: Dict[str, Dict[str, List[str]]] # {prop_type: {version: [prop1, prop2, ...]}}
            self.properties = json_dict["properties"]

        else:
            self.identity: str = identity # id of the entry
            self.folio: str = folio # folio of the entry
            self.xml: Dict[str, str] = {'tc': tc, 'tcn': tcn, 'tl': tl} # dict that contains xml strings keyed by version
            self.root = {k: self.make_etree(v) for k, v in self.xml.items()}
            self.txt = {'tc': self.text('tc'), 'tcn': self.text('tcn'), 'tl': self.text('tl')} # dict that contains txt strings keyed by version
            self.title = {k: self.find_title(k) for k, _ in self.xml.items()}
            self.categories: List[str] = self.find_categories()
            self.length = {k: self.clean_length(k) for k, _ in self.xml.items()}

            self.properties: Dict[str, Dict[str, List[str]]] # {prop_type: {version: [prop1, prop2, ...]}}
            self.properties = self.find_all_properties()

        self.margins = self.find_margins()
        self.del_tags = self.find_del()
        self.captions = {k: self.find_captions(k) for k in self.xml.keys()}

    def make_etree(self, xml_string: str):
        xml_string = f"<entry>{xml_string}</entry>"
        # ^^ this is temporary band-aid code to stave off a larger problem.
        # see: https://github.com/cu-mkp/manuscript-object/issues/33.
        return et.XML(xml_string.encode())

    def find_categories(self) -> List[str]:
        """
       Find categories tagged in the div tag. Since categories are the same for each version,
        the 'tl' version is used.

        Inputs:
          text: str -- the tl version of the manuscript with xml tags
        Output:
          List[str] -- A list of the categories
        """
        
        categories = self.root['tl'].find('div').attrib.get('categories')
        if categories:
            return categories.split(';')
        return []

    def find_title(self, version: str, remove_del_text=False) -> str:
        """ 
        Use a regex to find text in between head tags. Specifying the version is not necessary since it is
        included in the dict comprehension statement where this function is called.

        Inputs:
          text: str -- the text of the entry with xml tags
        Output:
          str -- title text
        """
        root = self.root[version] 
        sups = root.findall(".//sup")
        for sup in sups:
            sup.text = "[" + sup.text + "]" # mark editor supplied titles with square brackets

        titles = root.findall(".//head")
        if not titles:
            return ''
        else:
            title = titles[0]
            if remove_del_text:
                title = self.prepare_txt(title)
            return et.tostring(title, method="text", encoding="utf-8").decode()

    def clean_length(self, version: str) -> int:
        # TODO: make it word count instead of character count.
        return len(self.txt[version])

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
        return [et.tostring(tag, method="text", encoding="utf-8").decode().replace("\n", " ") for tag in tags]

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
            for version in self.xml:
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
        for version in self.xml.keys():
            margin_list = []
            root = self.root[version] 
            for ab in [ab for ab in root.findall("ab") if ab.attrib.get("margin")]:
                margin_list.append(Margin(self.identity, ab.attrib.get("margin"), ab.text, ab.attrib.get("render")))
            margins[version] = margin_list
        return margins

    def find_del(self) -> List[str]:
        return [tag.text for tag in self.root["tl"].findall(".//del")]

    def find_captions(self, version: str) -> List[str]:
        return [tag.text for tag in self.root[version].findall(".//caption")]

    def prepare_txt(self, root: et.Element) -> et.Element:
        # see https://github.com/cu-mkp/m-k-manuscript-data/issues/1613 for discussion on this matter
        for deltag in root.findall(".//del"):
            deltag.text = '<-' if not deltag.text else f'<-{deltag.text}' # add <- before current content
            deltag.tail = '->' if not deltag.tail else f'->{deltag.tail}' # add -> before next content
        for illtag in root.findall(".//ill"):
            if illtag.text:
                print(illtag.text)
            illtag.text = "[illegible]"
        return root

    def text(self, version: str, xml: bool = False) -> str:
        """ Getter method for text based on version, xml. """
        if xml:
            return self.xml[version]
        else:
            root = self.prepare_txt(self.root[version]) # e.g. add <- -> to text within <del> tags
            return et.tostring(root, method="text", encoding="utf-8").decode()

"""
    def context(self, term: str, version: str) -> str:
        # Returns five words on either side of the given term in the specified version. 
        text = self.text(version).lower()
        if term in text:
            #TODO: clean up this regex
            context = re.search(fr'((\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?{term}(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?)', text)
            if context:
                return context[0]
        return f'{term} not found in {version} {self.identity}'
"""
