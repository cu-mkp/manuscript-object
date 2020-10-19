from typing import List, Dict
from lxml import etree as et
import utils

# stylesheet to use for XSLT transformations
transform = et.XSLT(et.parse("annotations.xslt"))

# module-level functions for helping parse xml inside entries

def generate_etree(xml_string: str) -> et.Element:
    # given a string of valid XML, generate an XML etree object for easier XML parsing
    return et.fromstring(xml_string)

def to_xml_string(xml: et.Element) -> str:
    # take in an XML etree and render it as decoded utf-8 text, with tags and all
    return et.tostring(xml, encoding="utf-8", pretty_print=False).decode()

def to_string(xml: et.Element, *args, **kwargs) -> str:
    # take in an XML etree and convert it to text (remove all tags)
    # by default, use all editorial annotations
    # TODO: ask for a better term than "annotations" -- they're not tags, what are they?

    return xslt_transform(xml, *args, **kwargs)

def xslt_transform(xml: et.Element, *args, **kwargs) -> str:
    # takes an etree element and returns an etree element with added annotations
    # e.g. adding <- -> around deleted text, or add "[illegible]" in <ill> tags

    # XSLT booleans are represented as "true()" and "false()"
    for k,v in kwargs.items():
        if v==True:
            kwargs[k] = "true()"
        elif v==False:
            kwargs[k] = "false()"

    return str(transform(xml, *args, **kwargs))

def parse_categories(xml: et.Element) -> List[str]:
    # get the categories attribute of the first div in the TL version
    categories = xml.find('div').get('categories')
    if categories:
        return categories.split(";")
    else:
        return []

def find_terms(xml: et.Element, tag: str, *args, **kwargs) -> List[str]:
    # takes an etree element to search
    # returns a list of all terms with a given tag, in plaintext
    tags = xml.findall(f".//{tag}")
    return [to_string(tag, **kwargs).replace("\n", " ") for tag in tags]

def parse_properties(xml: et.Element) -> Dict[str, List[str]]:
    # {prop1: [term1, term2, ...], prop2: [term1, term2, ...], ...}
    properties = {}
    for prop, tag in utils.prop_dict.items():
        properties[prop] = find_terms(xml, tag)
    return properties

def find_title(xml: et.Element) -> str:
    # get the first "head" term in plaintext with annotations
    # if none are found, return an empty string

    titles = find_terms(xml, "head", {"del":"false()"}) # exclude del annotations
    if titles:
        return titles[0]
    else:
        return ''

def find_identity(xml: et.Element) -> str:
    # find the identity in the etree
    # parse the etree to find the first div
    # if div has an id attribute, return it; otherwise return empty string
    div = xml.find('div')
    if len(div):
        identity = div.get('id')
        return identity if identity else ''
    else:
        return ''

class Entry:
    def __init__(self, xml, identity=None, folio=None):
        # constructor: generate instance variables from xml string
        # identity: str
        # folio: str
        # xml: lxml.etree.Element object

        # all the important data is enclosed in a dictionary called 'data'
        # this makes it really easy to access!
        self.data = {}
        self.data["xml"] = xml #TODO: confirm that this is really the best name for this

        self.data["identity"] = identity if identity else find_identity(self.xml) # if you're not given an identity, you can try to discern it from the id attribute of the first div
        self.data["folio"] = folio if folio else "" # if you're not given a folio, don't try to guess!

        self.data["text"] = to_string(self.xml)
        self.data["xml_string"] = to_xml_string(self.xml) #TODO: find a better name for this?

        self.data["title"] = find_title(self.xml)

        self.data["categories"] = parse_categories(self.xml)
        self.data["properties"] = parse_properties(self.xml)

    @classmethod
    def from_file(cls, filename: str, identity=None, folio=None):
        # altnernative constructor: read from a given file path and use the contents of that file as the xml
        return cls(et.parse(filename), identity=identity, folio=folio)

    @classmethod
    def from_string(cls, xml_string, identity=None, folio=None):
        # alternative constructor: read from a string of valid XML
        xml = generate_etree(xml_string)
        return cls(xml, identity=identity, folio=folio)

    def as_dict(self):
        # return the data dictionary of the entry object
        return self.data

    def __len__(self) -> int:
        return len(self.text)

    def __getattr__(self, attr):
        # allows you to write, e.g. "entry.properties" and get the value of that key in the data dict
        # this is really cool, trust me!
        return self.data.get(attr)

    def __repr__(self):
        return repr(self.as_dict())

    #TODO: context function to get text around a particular term
