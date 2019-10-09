import re
from typing import List, Dict
from collections import OrderedDict

re_tags = re.compile(r'<.*?>') # selects any tag
re_head = re.compile(r'<head>(.*?)</head>')
re_materials = re.compile(r'<m>(.*?)<\/m>') # selects text between materials tags
attribute_dict = {'animal': 'al', 'body_part': 'bp', 'currency': 'cn', 'definition': 'def',
              'environment': 'env', 'material': 'm', 'medical': 'md', 'measurement': 'ms',
              'music': 'mu', 'plant': 'pa', 'place': 'pl', 'personal_name': 'pn',
              'profession': 'pro', 'sensory': 'sn', 'tool': 'tl', 'time': 'tmp'}
attribute_dict_reverse = {v: k for k, v in attribute_dict.items()}

class Recipe:

    def __init__(self, identity: str, tc: str, tcn: str, tl: str) -> None:
        
        self.identity: str = identity # id of the entry
        self.versions: Dict[str, str] = {'tc': tc, 'tcn': tcn, 'tl': tl} # dict that contains xml text
        self.title: Dict[str, str] = {'tc': self.get_head(tc),
                                     'tcn': self.get_head(tcn),
                                     'tl': self.get_head(tl)}
        self.length: Dict[str, int] = {k: len(self.text(k)) for k, v in self.versions.items()} 
        self.attributes: Dict[str, Dict[str, List[str]]] # {attribute_type: {version: [attribute1, attribute2, ...]}}
        self.attributes = {k: {} for k in attribute_dict.keys()}
        self.margins = self.get_margins()
        for k, v in attribute_dict.items():
            self.attributes[k] = self.find_tag(v)
        self.balanced: Dict[str: bool] = {k: self.check_balance(k) for k in self.versions.keys()}

    def get_margins(self):
        # include figure id?
        # do we record placement of margins?
        margins = re.findall(r'(<ab margin="[\w-]*"( render="tall")?>(.?)</ab>)', self.versions['tl'])
        return [m[0] for m in margins] if margins else []

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
            tagged_dict[k] = list(set([re_tags.sub('', t).lower() for t in re_tagged.findall(v)]))
        return tagged_dict

    def get_attribute(self, attribute, version='tl'):
        """ Getter method for attribute based on version. """
        return self.attributes[attribute][version]

    def thesaurus_swap(self, old_term, new_term, attribute):
        """ Removes an old term from the dictionary, and adds the new term. """
        self.attributes[attribute]['tl'].remove(old_term)
        self.attributes[attribute]['tl'].append(new_term)

    def check_balance(self, version) -> bool:
        #TODO: update
        tags = re_tags.findall(self.text(version, True))
        tags = [t for t in tags if 'cont' not in t and 'lb' not in t]
        stack = []
        for tag in tags:
            if '</' in tag:
                if len(stack) < 1 or tag.replace('/', '') != stack.pop():
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
