import os

manuscript_data_path = os.path.join(os.path.dirname(os.getcwd()), "m-k-manuscript-data") # default m&k data directory
ms_xml_path = os.path.join(manuscript_data_path, "ms-xml")

versions = ['tc', 'tcn', 'tl']

prop_dict = {
    'animal': 'al',
    'body_part': 'bp',
    'currency': 'cn',
    'definition': 'df',
    'environment': 'env',
    'material': 'm',
    'medical': 'md',
    'measurement': 'ms',
    'music': 'mu',
    'plant': 'pa',
    'place': 'pl',
    'personal_name': 'pn',
    'profession': 'pro',
    'sensory': 'sn',
    'tool': 'tl',
    'time': 'tmp',
    'weapon': 'wp',
    'german': 'de',
    'greek': 'el',
    'italian': 'it',
    'latin': 'la',
    'occitan': 'oc',
    'poitevin': 'po'
}

categories = [
    "lists",
    "medicine",
    "stones",
    "varnish",
    "arms and armor",
    "casting",
    "metal process",
    "practical optics",
    "decorative",
    "painting",
    "glass process",
    "household and daily life",
    "tool",
    "wood and its coloring",
    "cultivation",
    "merchants",
    "dyeing",
    "preserving",
    "tricks and sleight of hand",
    "corrosives",
    "animal husbandry",
    "wax process",
    "printing",
    "alchemy",
    "La boutique",
    "manuscript structure" 
]

with open("annotations.xslt", "r") as fp:
    stylesheet = fp.read()
