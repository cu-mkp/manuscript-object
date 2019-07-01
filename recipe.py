import re
from typing import List, Dict

re_tags = re.compile(r'<.*?>') # selects any tag
re_materials = re.compile(r'<m>(.*?)<\/m>') # selects text between materials tags
attribute_dict = {'animal': 'al', 'body_part': 'bp', 'currency': 'cn', 'definition': 'def',
              'environment': 'env', 'material': 'm', 'medical': 'md', 'measurement': 'ms',
              'music': 'mu', 'plant': 'pa', 'place': 'pl', 'personal_name': 'pn',
              'profession': 'pro', 'sensory': 'sn', 'tool': 'tl', 'time': 'tmp'}

class Recipe:

    def __init__(self, identity: str, tc: str, tcn: str, tl: str) -> None:
        self.identity: str = identity # id of the entry
        self.versions: Dict[str, str] = {'tc': tc, 'tcn': tcn, 'tl': tl} # dict that contains xml text
        self.length: Dict[str, int] = {k: len(self.text(k)) for k, v in self.versions.items()} 

        self.attributes: Dict[str, Dict[str, List[str]]]
        self.attributes = {k: {} for k in attribute_dict.keys()}
        for k, v in attribute_dict.items():
            self.attributes[k] = self.find_tag(v)
        self.balanced: Dict[str: bool] = {k: self.check_balance(k) for k in self.versions.keys()}

    def text(self, version: str, xml: bool = False) -> str:
        return self.versions[version] if xml else re_tags.sub('', self.versions[version])

    def find_tag(self, tag: str):
        re_tagged = re.compile(rf'<{tag}>(.*?)<\/{tag}>')
        tagged_dict = {}
        for k, v in self.versions.items():
            tagged_dict[k] = [re_tags.sub('', t).lower() for t in re_tagged.findall(v)]
        return tagged_dict

    def get_attribute(self, attribute, version='tl'):
        return self.attributes[attribute][version]

    def check_balance(self, version) -> bool:
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
        text = self.text(version).lower()
        if term in text:
            context = re.search(fr'((\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?{term}(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?(\s\w*)?)', text)
            if context:
                return context[0]
        return f'{term} not found in {version} {self.identity}'
