from typing import List, Dict, OrderedDict
from lxml import etree as et
import utils

# stylesheet to use for XSLT transformations
transform = et.XSLT(et.parse(utils.stylesheet_path))

def generate_etree(xml_string: str) -> et.Element:
    """Generate an XML etree object for easier XML parsing.
    Input: a string of valid XML
    Output: lxml.etree.Element object
    """
    return et.fromstring(xml_string)

def to_xml_string(xml: et.Element) -> str:
    """Render an XML etree as decoded utf-8 text, with tags."""
    return et.tostring(xml, encoding="utf-8", pretty_print=False).decode()

def to_string(xml: et.Element, params={}) -> str:
    """Convert an XML etree to text, removing all tags and rendering editorial tags.
    Uses global variable `transform`.
    """
    return xslt_transform(xml, transform, params=params)

def xslt_transform(xml: et.Element, transform: et.XSLT, params={}) -> str:
    """Apply an XSLT stylesheet to the given XML etree, rendering it as a string.
    Optional argument `params` is a dictionary specifying XSLT parameters.
    Editorial tags are rendered according to specification here: https://github.com/cu-mkp/m-k-manuscript-data/issues/1613#issuecomment-700295493.
    Uses global variable `transform`.
    """
    return str(transform(xml, **params))

def parse_categories(xml: et.Element) -> List[str]:
    """Get the categories attribute of the first div.
    Further divs are merely continuations of the same entry, hence only getting the categories attribute of the first div will suffice.
    """
    categories = xml.find('div').get('categories')
    if categories:
        return categories.split(";")
    else:
        return []

def find_terms(xml: et.Element, tag: str, params={}) -> List[str]:
    """Returns a list of the contents of every instance of a given tag in an XML etree, rendered as plaintext using the to_string() function."""
    tags = xml.findall(f".//{tag}")
    return [to_string(tag, params=params).replace("\n", " ") for tag in tags]

def parse_properties(xml: et.Element) -> Dict[str, List[str]]:
    """Return a dictionary keyed by property containing a list of the contents of all tags for that property.
    Returned object has the following schema:
        {prop1: [term1, term2, ...], prop2: [term1, term2, ...], ...}
    """
    properties = OrderedDict()
    for prop, tag in utils.prop_dict.items():
        properties[prop] = find_terms(xml, tag)
    return properties

def find_title(xml: et.Element) -> str:
    """Get the content of the first "head" tag, rendered in plaintext, but not rendering "del" editorial tags.
    If no such tags are found, return an empty string.
    """
    titles = find_terms(xml, "head", params={"del":"'omit'"}) # Remove text inside <del> tags from the title.
    if titles:
        return titles[0]
    else:
        return ''

def find_identity(xml: et.Element) -> str:
    """Get the identity attribute of the first div in the given XML etree.
    If there is no such attribute, return an empty string.
    """
    div = xml.find('div')
    if div is not None and len(div):
        return div.get('id') or ''
    else:
        return ''

class Entry:
    def __init__(self, xml: et.Element, identity: str=None, folio: str=None):
        """
        Generate a dictionary full of useful data by parsing the given XML etree.
        """

        self.data = {}
        self.data["xml"] = xml

        self.data["identity"] = identity or find_identity(self.xml) # if you're not given an identity, you can try to discern it from the id attribute of the first div
        self.data["folio"] = folio or "" # if you're not given a folio, don't try to guess!

        self.data["text"] = to_string(self.xml)
        self.data["xml_string"] = to_xml_string(self.xml)

        self.data["title"] = find_title(self.xml)

        self.data["categories"] = parse_categories(self.xml)
        self.data["properties"] = parse_properties(self.xml)

    @classmethod
    def from_file(cls, filename: str, identity=None, folio=None):
        """Alternative constructor: read from a given file path and use the contents of that file as the XML."""
        return cls(et.parse(filename), identity=identity, folio=folio)

    @classmethod
    def from_string(cls, xml_string, identity=None, folio=None):
        """Alternative constructor: read from a string of valid XML."""
        xml = generate_etree(xml_string)
        return cls(xml, identity=identity, folio=folio)

    def as_dict(self):
        """Return the data dictionary."""
        return self.data

    def __len__(self) -> int:
        """Return the length of the plaintext version of the entry, with full editorial tag renditions.
        This is somewhat arbitrary; we could also return the length of the XML string.
        """
        return len(self.text)

    def __getattr__(self, attr):
        """For convenience, make data dictionary values accessible by treating attributes as keys.
        E.g. `entry.properties` returns the value of that key in the data dict, effectively `entry.data["properties"]`.
        """
        return self.data.get(attr)

    def __repr__(self):
        return repr(self.as_dict())

    #TODO: context function to get text around a particular term
