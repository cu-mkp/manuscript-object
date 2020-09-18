from typing import List, Dict 
from lxml import etree as et
import utils

class Recipe:

    #TODO: make all of these methods external functions
    def __init__(self, xml, identity=None, folio=None):
        # identity: str
        # folio: str
        # xml: str -- string containing *well-formed* raw XML
        self.xml = xml

        self.etree = self.generate_etree()
        
        self.identity = identity if identity else self.find_identity() # if you're not given an identity, you can try to discern it from the id attribute of the first div
        self.folio = folio if folio else "" # if you're not given a folio, don't try to guess! 
        
        self.text = self.to_text(self.etree, annotate=True)

        self.title = self.find_title()

        self.categories = self.parse_categories() 
        self.properties = self.parse_properties() 

    @classmethod
    def from_file(cls, filename: str, identity=None, folio=None):
        with open(filename, "r") as fp:
            xml = fp.read().encode()
        return cls(xml, identity=identity, folio=folio)

    def as_dict(self):
        return self.__dict__

    def generate_etree(self) -> et.Element:
        return et.fromstring(self.xml)

    def to_text(self, xml: et.Element, annotate=False) -> str:
        if annotate:
            xml = self.add_annotations(xml) # e.g. add <- -> to text within <del> tags
        return et.tostring(xml, method="text", encoding="utf-8").decode()

    def __len__(self) -> int:
        return len(self.text)

    def parse_categories(self) -> List[str]:
        # get the categories attribute of the first div in the TL version
        categories = self.etree.find('div').attrib.get('categories')
        if categories:
            return categories.split(";")
        else:
            return []

    def find_terms(self, xml: et.Element, tag: str, annotate=False) -> List[str]:
        # takes an etree element to search
        # returns a list of all terms with a given tag, in plaintext
        tags = xml.findall(f".//{tag}")
        return [self.to_text(tag, annotate=annotate).replace("\n", " ") for tag in tags]
        #TODO: annotate terms or no?

    def parse_properties(self) -> Dict[str, List[str]]:
        # {prop1: [term1, term2, ...], prop2: [term1, term2, ...], ...}
        properties = {}
        for prop, tag in utils.prop_dict.items():
            properties[prop] = self.find_terms(self.etree, tag)
        return properties

    def find_title(self) -> str:
        titles = self.find_terms(self.etree, "head", annotate=True)
        if titles:
            return titles[0]
        else:
            return ''

    def find_identity(self) -> str:
        div = self.etree.find('div')
        if len(div):
            identity = div.attrib.get('id')
            return identity if identity else ''
        else:
            return ''

    def add_annotations(self, xml: et.Element) -> et.Element:
        # takes an etree element and returns an etree element with added annotations
        # e.g. adding <- -> around deleted text, or add "[illegible]" in <ill> tags
        # see https://github.com/cu-mkp/m-k-manuscript-data/issues/1613 for discussion on this matter
        for deltag in xml.findall(".//del"):
            deltag.text = '<-' if not deltag.text else f'<-{deltag.text}' # add <- before current content
            deltag.tail = '->' if not deltag.tail else f'->{deltag.tail}' # add -> before next content
        for illtag in xml.findall(".//ill"):
            if illtag.text:
                print(illtag.text)
            illtag.text = "[illegible]"

        for suptag in xml.findall(".//sup"):
            suptag.text = '[' if not suptag.text else f'[{suptag.text}'
            suptag.tail = ']' if not suptag.tail else f']{suptag.tail}'

        return xml

    #TODO: context function to get text around a particular term
