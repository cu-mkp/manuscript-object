import pandas as pd
from digital_manuscript import BnF

manuscript = BnF()
df = pd.DataFrame(columns=['entry_id', 'version', 'position', 'render', 'length'])

i = 0
for identity, entry in manuscript.entries.items():
    if len(entry.margins) > 0:
        for version, margin_list in entry.margins.items():
            for margin in margin_list:
                df.loc[i] = [identity, version, margin.position, margin.render, margin.length]
                i += 1

df.to_csv('margins.csv', index=False)
