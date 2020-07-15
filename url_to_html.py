import urllib2

def url_to_html(url:str) -> str:
    """
    Get the full html from a given url.
    """
    page = urllib.request.urlopen(url)      # open url
    return page.read().decode('utf-8')     # decode to text