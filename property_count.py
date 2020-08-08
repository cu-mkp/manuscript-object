# %%
import os
import pandas as pd

# %%
# fun fact: I used code to write this code for me
prop_dict = {
    'animal':'al',
    'body_part':'bp',
    'currency':'cn',
    'definition':'df',
    'environment':'env',
    'material':'m',
    'medical':'md',
    'measurement':'ms',
    'music':'mu',
    'plant':'pa',
    'place':'pl',
    'personal_name':'pn',
    'profession':'pro',
    'sensory':'sn',
    'tool':'tl',
    'time':'tmp',
    'weapon':'wp',
    'german':'de',
    'greek':'el',
    'italian':'it',
    'latin':'la',
    'occitan':'oc',
    'poitevin':'po',
}

versions = ['tc', 'tcn', 'tl']

# %%
base = os.path.dirname(os.getcwd()) # .../m-k-manuscript-data/"
entry_metadata_path = base + "/metadata/entry_metadata.csv"
output_path = "property_count.csv"

# %%
df = pd.read_csv(entry_metadata_path)

# %%
naughty_list = pd.DataFrame(columns=["entry_id", "prop", "counts", "tc", "tcn", "tl"])

for _, row in df.iterrows(): # entry by entry
    for prop in prop_dict.values(): # property by property
        counts = [0,0,0]
        for i, version in enumerate(versions): # compare the three versions
            terms = row[f'{prop}_{version}'] # get the ";"-separated terms
            if type(terms)==str: # skip if "nan" in df (i.e. if blank, i.e. no terms)
                counts[i] = len(terms.split(";")) # count the terms and save it to compare between versions
        # this weird-looking condition checks if all the elements in a list are identical
        if counts.count(counts[0]) != len(counts):
            print("Unequal property counts in entry " + row['div_id'] + ", property " + prop)
            print(counts)
            naughty_list = naughty_list.append({
                "entry_id" : row['div_id'],
                "prop" : prop,
                "counts" : counts,
                "tc" : row[prop + "_tc"],
                "tcn": row[prop + "_tcn"],
                "tl" : row[prop + "_tl"],
            }, ignore_index=True)

# %%
naughty_list.to_csv(output_path, index=False)