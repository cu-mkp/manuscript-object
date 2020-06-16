import os
import sys
import pandas as pd
import re
#from urllib.error import HTTPError
from url_to_html import url_to_html, HTTPError

# Setup
target_website = 'drive.google.com'     # the website to look for when filtering down hrefs

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' in cwd else f'{cwd}/manuscript-object/'     # this validation is probably not necessary
fieldnotes_metadata_file = 'FA18+other-fieldnotes-list+links.csv'
in_path = f'{m_path}/fieldnotes/{fieldnotes_metadata_file}'
out_path = f'{m_path}/fieldnotes/fieldnotes_hrefs.csv'

url_column = 'full-html'
hrefs_column = 'references'

regex = re.compile(r'<a href="(https?://.*?)".*?>')       # regex to find http hrefs in a block of html
#regex = re.compile(r'<a href="(.*?)".*?>')       # regex to find hrefs in a block of html (not necessarily web links)

def process_url(url:str, pattern:re.Pattern, target:str) -> str:
    try:
        html = url_to_html(url) # Get html from a given url
        matches = pattern.findall(html) # Find all regex matches in html according to given pattern
        matches = [match for match in matches if target in match] # Filter the matches to those which contain a particular target string
        return ','.join(matches) if matches else 'none' # Convert this list of matches to a comma-separated string
    except HTTPError:
        return 'url not found'
    except ValueError:
        return 'not a valid web address'
    
def get_links(to_csv=False):
    """
    Add a column to field notes CSV containing all the href links to a particular target website.
    Optionally write this new CSV.
    Return the pandas DataFrame representing this new CSV.
    """
    fieldnotes = pd.read_csv(in_path)
    fieldnotes[hrefs_column] = fieldnotes[url_column].apply(lambda url: process_url(url, regex, target_website))
    
    if to_csv:
        fieldnotes.to_csv(out_path, index=False)
        
    return fieldnotes

# Run script
if __name__=="__main__":
    get_links(to_csv=True)