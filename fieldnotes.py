import os
import pandas as pd
import re
import urllib.request
from urllib.error import HTTPError

# Setup

target_website = 'drive.google.com'     # the website to look for when filtering down hrefs

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' in cwd else f'{cwd}/manuscript-object/'     # this validation is probably not necessary
fieldnotes_metadata_file = 'FA18+other-fieldnotes-list+links.csv'
in_path = f'{m_path}/fieldnotes/{fieldnotes_metadata_file}'
out_path = f'{m_path}/fieldnotes/fieldnotes_hrefs.csv'

url_column = 'full-html'
hrefs_column = 'references'

re_href = re.compile(r'<a href="(https?://.*?)".*?>')       # regex to find http hrefs in a block of html
#re_href = re.compile(r'<a href="(.*?)".*?>')       # regex to find hrefs in a block of html (not necessarily web links)

# Function

def get_regex_from_url(url:str, regex, target:str='') -> str:
    """
    Return all text from a given url matching a given regex and containing a given target string.
    Text is returned as a string with elements separated by commas.
    Will return appropriate error messages as strings in case of invalid url.
    
    Inputs:
      url: A string representing a url.
      regex: A regex Pattern object which determines what text to extract from the html of the url.
      target: A filtering string. Regex matches will only be included in the output if they include this string.
              Defaults to the empty string (i.e. defaults to no filter).
    
    Outputs:
      String consisting of each element found via regex and filtered via target, separated by commas.
            Ex: 'https://makingandknowing.org,https://columbia.edu'
    """
    try:
        page = urllib.request.urlopen(url)      # open url
    except HTTPError:
        return 'url not found'
    except ValueError:
        return 'not a valid web address'
    
    page_text = page.read().decode('utf-8')     # decode to text
    
    matches = [href for href in regex.findall(page_text) if target in href]     # get hrefs linking to target
    
    if not matches:
        return 'none'       # if target nowhere in that url, return 'none'
    else:
        return ','.join(matches)        # otherwise return a string containing each href separated by commas

# Script

fieldnotes = pd.read_csv(in_path)
fieldnotes[hrefs_column] = fieldnotes[url_column].apply(lambda url: find_hrefs_from_url(url, re_href, target=target_website))

fieldnotes.to_csv(out_path, index=False)