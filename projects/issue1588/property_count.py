# %%
# imports
import os
import pandas as pd

# %%
# set up variables
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
# set up paths
base = os.path.dirname(os.getcwd()) # .../m-k-manuscript-data/"
entry_metadata_path = base + "/metadata/entry_metadata.csv"
output_path = "property_count.csv"

# %%
# load spreadsheet into DataFrame
df = pd.read_csv(entry_metadata_path)

# %%
# count properties
naughty_list = pd.DataFrame(columns=["entry_id", "prop", "counts", "tc", "tcn", "tl"])
counts = []

for _, row in df.iterrows(): # entry by entry
    
    for prop in prop_dict.values(): # property by property
        counts.append([0,0,0])
        
        for j, version in enumerate(versions): # compare the three versions
            terms = row[f'{prop}_{version}'] # get the ";"-separated terms
            
            if type(terms)==str: # skip if "nan" in df (i.e. if blank, i.e. no terms)
                counts[-1][j] = len(terms.split(";")) # count the terms and save it to compare between versions
                
        # check if the min and max are identical (i.e. all counts identical)
        if min(counts[-1]) != max(counts[-1]):
            print("Unequal property counts in entry " + row['div_id'] + ", property " + prop)
            print(counts[-1])
            
            naughty_list = naughty_list.append({
                "entry_id" : row['div_id'],
                "prop" : prop,
                "counts" : counts[-1],
                "tc" : row[prop + "_tc"],
                "tcn": row[prop + "_tcn"],
                "tl" : row[prop + "_tl"],
            }, ignore_index=True)

# %%
# analysis of counts
gt = lambda y: len([x for x in counts if abs(min(x) - max(x)) > y])
gt3 = gt(3)
gt2 = gt(2) - gt3
gt1 = gt(1) - gt2
gt0 = gt(0) - gt1

print("number of entries:", df.shape[0])
print("=================")
total = naughty_list.shape[0]
print(f"total mismatched: {total}")
print(f">0: {gt0} ({round(gt0/total * 100)}%)")
print(f">1: {gt1} ({round(gt1/total * 100)}%)")
print(f">2: {gt2} ({round(gt2/total * 100)}%)")
print(f">3: {gt3} ({round(gt3/total * 100)}%)")

# %%
# save results to spreadsheet
naughty_list.to_csv(output_path, index=False)
print("saved successfully")