import re
from typing import List, Dict, Optional
from collections import OrderedDict

re_tags = re.compile(r'<.*?>') # selects any tag
re_head = re.compile(r'<head>(.*?)</head>')
re_materials = re.compile(r'<m>(.*?)<\/m>') # selects text between materials tags
prop_dict = {'animal': 'al', 'body_part': 'bp', 'currency': 'cn', 'definition': 'def',
              'environment': 'env', 'material': 'm', 'medical': 'md', 'measurement': 'ms',
              'music': 'mu', 'plant': 'pa', 'place': 'pl', 'personal_name': 'pn',
              'profession': 'pro', 'sensory': 'sn', 'tool': 'tl', 'time': 'tmp', 'weapon': 'wp'}
prop_dict_reverse = {v: k for k, v in prop_dict.items()}

class Recipe:

    def __init__(self, identity: str, tc: str, tcn: str, tl: str) -> None:
        self.identity: str = identity # id of the entry
        self.versions: Dict[str, str] = {'tc': tc, 'tcn': tcn, 'tl': tl} # dict that contains xml text
        
        self.continued = True if 'continued="yes">' in self.versions['tl'] else False

        self.title: Dict[str, str] = {'tc': self.get_head(tc),
                                     'tcn': self.get_head(tcn),
                                     'tl': self.get_head(tl)}
        self.length: Dict[str, int] = {k: len(self.text(k)) for k, v in self.versions.items()} 
        self.properties: Dict[str, Dict[str, List[str]]] # {prop_type: {version: [prop1, prop2, ...]}}
        self.properties = {k: {} for k in prop_dict.keys()}
        for k, v in prop_dict.items():
            self.properties[k] = self.find_tag(v)
        self.margins = self.find_margins()
        self.del_tags = self.find_del()
        self.captions = {k: self.find_captions(k) for k in self.versions.keys()}
        self.balanced: Dict[str: bool] = {k: self.check_balance(k) for k in self.versions.keys()}
        

    def find_margins(self) -> List[str]:
        # include figure id?
        # {'tc': (margin1 placement, margin1text), (margin2 placement, margin2 text),
        #   ...}
        margins = {}
        for version in self.versions.keys():
          ver_list = []
          search = re.findall(r'<ab margin="([\w-]*)"( render="([\w-]*)")?>(.*?)<\/ab>', self.versions[version])
          for tup in search:
              assert isinstance(tup[0], str) and isinstance(tup[1], str)
            #   print(tup)
              ver_list.append(tup)
              
          margins[version] = ver_list
        return margins

    def find_del(self) -> List[str]:
        d = re.findall(r'<del>(.*?)</del>', self.versions['tl'])
        return d if d else []

    def find_captions(self, version: str) -> List[str]:
        c = re.findall(r'<caption>(.*?)</caption>', self.versions[version])
        return c if c else []

    def get_head(self, text: str) -> str:
        """ search text for text in a <head> tag. """
        head = re_head.search(text)
        if head:
            return re_tags.sub('', head[0])
        return ''

    def get_identity(self) -> str:
        """ Getter method for identity. """
        return self.identity

    def text(self, version: str, xml: bool = False) -> str:
        """ Getter method for text based on version, xml. """
        return self.versions[version] if xml else re_tags.sub('', self.versions[version])

    def find_tag(self, tag: str) -> Dict[str, List[str]]:
        """
        For any given tag, finds all text within that tag.
        Returns data as a dict of the form {version: [tagged_str1, tagged_str2, ...]}
        """
        re_tagged = re.compile(rf'<{tag}>(.*?)<\/{tag}>')
        tagged_dict = {}
        for k, v in self.versions.items():
            tagged_dict[k] = list(set([re_tags.sub('', t).lower().strip() for t in re_tagged.findall(v)]))
        return tagged_dict

    def get_prop(self, prop, version='tl'):
        """ Getter method for prop based on version. """
        return self.properties[prop][version]

    def check_balance(self, version) -> bool:
        tags = re_tags.findall(self.text(version, True))
        tags = [t for t in tags if not any(word in t for word in ['comment', 'figure'])]
        tags = [re.sub(r' (margin|render|continued)="[\w-]*"', '', t) for t in tags]
        stack = []
        for tag in tags:
            if '</' in tag:
                if len(stack) < 1 or tag.replace('/', '') != stack.pop():
                    # print(self.identity, tags)
                    return False
            elif '/' not in tag and '!' not in tag:
                stack.append(tag)
        return True

    def context(self, term: str, version: str) -> str:
        """ Returns five words on either side of the given term in the specified version. """
        text = self.text(version).lower()
        if term in text:
            context = re.search(fr'((\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?{term}(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?)', text)
            if context:
                return context[0]
        return f'{term} not found in {version} {self.identity}'

    def head(self, version):
        """ Returns up to the first 50 characters of the manuscript."""
        head = self.text(version)
        if len(head) > 50:
            return head[:50]
        return head
