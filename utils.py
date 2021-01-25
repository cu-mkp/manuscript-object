import os

manuscript_data_path = os.path.join(os.path.dirname(os.getcwd()), "m-k-manuscript-data") # default m&k data directory
ms_xml_path = os.path.join(manuscript_data_path, "ms-xml")
versions = ['tc', 'tcn', 'tl']
version_paths = [os.path.join(ms_xml_path, version) for version in versions]
tc_path, tcn_path, tl_path = version_paths

ms_txt_path = os.path.join(manuscript_data_path, "ms-txt")
entries_path = os.path.join(manuscript_data_path,"entries")
all_folios_path = os.path.join(manuscript_data_path, "allFolios")
metadata_path = os.path.join(manuscript_data_path, "metadata")

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
    'french': 'fr',
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
