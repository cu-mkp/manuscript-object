from digital_manuscript import BnF
import os
import pandas as pd
import re
import urllib.request
from urllib.error import HTTPError

# Setup
manuscript = BnF()

cwd = os.getcwd()
#m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'
m_path = cwd if 'manuscript-object' in cwd else f'{cwd}/manuscript-object/'
fieldnotes_path = f'{m_path}/fieldnotes/FA18+other-fieldnotes-list+links.csv'
out_path = f'{m_path}/fieldnotes/fieldnotes_refs.csv'

df_url_column = 'full-html'
df_refs_column = 'references'

re_href = re.compile(r'<a href="(.*?)">') # get hyperlinked urls


# Script:

fieldnotes = pd.read_csv(fieldnotes_path)

references = [None] * len(fieldnotes[df_url_column])  # initialize list of proper length filled with falsy values
for i, url in enumerate(fieldnotes[df_url_column]):
    if 'http://' not in url:
        url = f'http://{url}'
        
    try:
        f = urllib.request.urlopen(url) # open url
    except HTTPError:
        print(f"URL not found: {url}")
        references[i] = 'url not found'
        continue
    
    page_text = f.read().decode('utf-8') # decode to text
    
    matches = re_href.findall(page_text) # find hyperlinks
    
    for match in matches:
        if 'drive.google.com' in match:
            if not references[i]:
                references[i] = match        # first url
            else:
                references[i] += ',' + match # append next url, separated by comma
    
    # if no hyperlinks in that fieldnote, enter 'none'
    if not references[i]:
        references[i] = 'none'

fieldnotes.insert(len(fieldnotes.columns), df_refs_column, references) # add the references as a column at the end

fieldnotes.to_csv(out_path, index=False)
