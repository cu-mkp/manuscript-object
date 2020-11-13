import os

manuscript_data_path = os.path.join(os.path.dirname(os.getcwd()), "m-k-manuscript-data") # default m&k data directory
ms_xml_path = os.path.join(manuscript_data_path, "ms-xml")
versions = ['tc', 'tcn', 'tl']
version_paths = [os.path.join(ms_xml_path, version) for version in versions]

prop_dict = {
    'animal': 'al',
    'body_part': 'bp',
    'currency': 'cn',
    'definition': 'def',
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
    'greek': 'ge',
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

stylesheet_path = "annotations.xslt"
