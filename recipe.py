import re
from typing import List, Dict, Optional
from collections import OrderedDict
from margin import Margin

re_tags = re.compile(r'<.*?>') # selects any tag
re_head = re.compile(r'<head( (margin|comment)="[\w-]*")?>(.*?)</head>')
re_materials = re.compile(r'<m>(.*?)<\/m>') # selects text between materials tags
prop_dict = {'animal': 'al', 'body_part': 'bp', 'currency': 'cn', 'definition': 'def',
              'environment': 'env', 'material': 'm', 'medical': 'md', 'measurement': 'ms',
              'music': 'mu', 'plant': 'pa', 'place': 'pl', 'personal_name': 'pn',
              'profession': 'pro', 'sensory': 'sn', 'tool': 'tl', 'time': 'tmp', 'weapon': 'wp'}
prop_dict_reverse = {v: k for k, v in prop_dict.items()}

class Recipe:

    def __init__(self, identity: str, folio: str, tc: str, tcn: str, tl: str) -> None:

        self.identity: str = identity # id of the entry
        self.folio: str = folio # folio of the entry
        self.versions: Dict[str, str] = {'tc': tc, 'tcn': tcn, 'tl': tl} # dict that contains xml text
        self.title = {k: self.find_title(v) for k, v in self.versions.items()}
        self.categories: List[str] = self.find_categories()
        self.length = {k: self.clean_length(v) for k, v in self.versions.items()}

        self.properties: Dict[str, Dict[str, List[str]]] # {prop_type: {version: [prop1, prop2, ...]}}
        self.properties = self.find_all_properties()

        self.margins = self.find_margins()
        self.del_tags = self.find_del()
        self.captions = {k: self.find_captions(k) for k in self.versions.keys()}

    def find_categories(self) -> List[str]:
        categories = re.search(r'categories="[\w\s;]*"', self.clean_text('tl'))
        if categories:
            return categories[0].split('"')[1].split(';')
        return []

    def find_title(self, text: str) -> str:
        """ search text for text in a <head> tag. """
        text = text.replace('<sup>', '[').replace('</sup>', ']') # mark editor supplied titles with square brackets
        text = re.sub(r'\s+', ' ', text.replace('\n', ' '))

        titles = re_head.search(text)
        return '' if not titles else re_tags.sub('', titles[0])

    def clean_length(self, text: str) -> int:
        text = re_tags.sub('', text)
        text = re.sub(r'\s+', ' ', text)
        return len(text)

    def find_tagged_text(self, text: str, tag: str) -> Dict[str, List[str]]:
        """
        For any given tag, finds all text within that tag.
        Returns data as a dict of the form {version: [tagged_str1, tagged_str2, ...]}
        """
        re_tagged = re.compile(rf'<{tag}>(.*?)<\/{tag}>')
        text = re.sub(r'\s+', ' ', text)

        tagged_text = list(set([str(re_tags.sub('', t).lower().strip()) for t in re_tagged.findall(text)]))
        return tagged_text

    def find_all_properties(self):
        all_properties = {}
        for prop, tag in prop_dict.items():
            p_dict = {}
            for version in self.versions:
                text = self.text(version, xml=True)
                p_dict[version] = self.find_tagged_text(text, tag)
            all_properties[prop] = p_dict
        return all_properties

                

            
    def clean_text(self, version: str):
        return re.sub(r'\s+', ' ', self.versions[version])

    def find_margins(self) -> List[str]:
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

    def get_identity(self) -> str:
        """ Getter method for identity. """
        return self.identity

    def text(self, version: str, xml: bool = False) -> str:
        """ Getter method for text based on version, xml. """
        if xml:
            return self.versions[version]

        text = self.versions[version].replace('\n', '**NEWLINE**')
        text = re_tags.sub('', text).replace('**NEWLINE**', '\n')
        text = re.sub(r'\n+', '\n\n', text)

        return text.strip(' \n')
       
    def original_text(self, version: str, xml: bool = False) -> str:
        """ Getter method for original text based on version, xml. """
        return self.originals[version] if xml else re_tags.sub('', self.originals[version]).strip()

    def find_tag(self, tag: str) -> Dict[str, List[str]]:
        """
        For any given tag, finds all text within that tag.
        Returns data as a dict of the form {version: [tagged_str1, tagged_str2, ...]}
        """
        re_tagged = re.compile(rf'<{tag}>(.*?)<\/{tag}>')
        tagged_dict = {}
        for version in self.versions.keys():
            tagged_dict[version] = list(set([re_tags.sub('', t).lower().strip() for t in re_tagged.findall(self.clean_text(version))]))
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

