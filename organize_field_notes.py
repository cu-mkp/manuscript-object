import os
import sys
import re
import urllib.request
import urllib.error
import urllib.parse
import csv
import unicodedata

# Variables
URL_PREFIX = "http://fieldnotes.makingandknowing.org/mainSpace"
ROOT_DIR = "C:/Users/grsch/Desktop/main"
SPACE_MENU = "space.menu.html"

ERROR_TABLE_PATH = "fieldnotes/errors.csv"

URL = 0        # url is first in regex Match tuple
TITLE = 1      # title is second in regex Match tuple

semesters_header = 'Course Archives'
re_semesters = re.compile(r'<li><a.*?href="(.*?)".*?>(.*?)</a></li>') # get url of each semester
re_intermediate = re.compile(r'<a.*?href="(.*?)".*?>(.*Field Notes.*|.*Annotations.*)</a>') # get url of intermediate field notes folder for a given semester
re_authors = re.compile(r'<a.*?href="(.*?)".*?>(.*?)</a>') # get url of each author for a given semester
re_fieldnotes = re.compile(r'<a.*?href="(.*?)".*?>(.*?)</a>') # get url of each field note for a given author

MAX_DEPTH = 4

REGEX = {
    0 : re_semesters,
    1 : re_intermediate,
    2 : re_authors,
    3 : re_fieldnotes
}

BAD_LIST = ['.pdf', '.docx', 'flickr.com', 'drive.google.com', 'docs.google.com', 'wiley.com', 'wikischolars.columbia.edu']

# Classes
class Node:

    def __init__(self, url, title, parent, depth):
        # print("parent: " + str(parent))
        # print("depth: " + str(depth))
        self.old_url = URL_PREFIX + "/" + url   # this is for making the final table; remains unchanged
        self.url = URL_PREFIX + "/" + url       # this is for working with the file; can be changed
        self.title = title
        self.parent = parent
        self.depth = depth
        self.has_error = self.check_error(self.url)
        if self.has_error:
            self.has_error = not self.repair_url()
        self.old_path = ROOT_DIR + urllib.parse.unquote(self.url)[len(URL_PREFIX):]    # I am somewhat ashamed of this code.
        self.new_path = self.make_new_path()
        # print(self.old_path[len(ROOT_DIR):] + " -> " + self.new_path[len(ROOT_DIR):])
        self.children = self.find_children()
        
    def check_error(self, url) -> bool:
        '''
        True -> url causes HTTP error
        False -> url is fine
        '''
        try:
            urllib.request.urlopen(url)
        except urllib.error.HTTPError:
            return True
        return False
    
    def repair_url(self) -> bool:
        '''
        Returns Boolean to indicate success of repairing url.
        !! This method modifies self.url !!!
        '''
        correction = ERROR_TABLE.get(self.old_url)
        if correction == None:
            return False
        elif correction != "?" and correction != "":
            self.url = correction
            # print(self.old_url + " corrected to " + correction)
            return not self.check_error(self.url)
        else:
            return False
            
    def make_new_path(self) -> str:
        if self.parent:
            parent_directory = os.path.dirname(self.parent.new_path)
        else:
            parent_directory = os.path.dirname(ROOT_DIR)  # should resolve to "C:/Users/grsch/Desktop"
        return parent_directory + "/" + self.sanitize(self.title).lower() + '/index.html'*(self.depth!=MAX_DEPTH) + '.html'*(self.depth==MAX_DEPTH)
    
    def sanitize(self, text):
        old = text
        if self.old_url == "http://fieldnotes.makingandknowing.org/mainSpace/Field%20Notes%20-%20Spring%202016.html":
            tmp = text.partition(',')
            text = tmp[2] + " " + tmp[0]     # fix "LastName, FirstName" situations (maybe)
            
        disallowed = ['.', ':', ',', ';', '/', '\\', '\'', '"', '#', '<', '>', '|', '*', '?']      # remove these invalid symbols
        for symbol in disallowed:
            text = text.replace(symbol, '')
            
        text = re.sub(r"\s+", ' ', text)  # replace multiple whitespace with just one space
        text = text.strip()  # remove leading and trailing whitespace
            
        # specific replacements for style
        replacements = {' - ':'_', ' ':'-', '%20':'-', '&amp':'+', '&':'+', 'é':'e'}
        for k,v in replacements.items():
            text = text.replace(k, v)
            
        # get canonical decomposition of unicode text, then re-encode to ascii while ignoring errors
        # in particular we hope this handles 'e%CC%81' and turns it into 'e'
        # text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
        
        return text
    
    def find_children(self):
        children = []
        depth = self.depth   # We have to define this separately for stupid edge-case reasons. :(
        
        if self.has_error:
            return children
        
        text = self.get_html()
        
        # hard-coded edge cases because I can't be bothered
        if depth == 0:
            text = text.partition("Course Archives")[2]     # on space.menu.html, only get links under "Course Archives"
        
        # specific pages:
        if self.url == "http://fieldnotes.makingandknowing.org/mainSpace/Fall%202014%20Archives.html":
            depth += 2     # pretend we're in the list of fieldnotes already. We will add the outer folder later. It will be horrible.
        elif self.url == "http://fieldnotes.makingandknowing.org/mainSpace/Spring%202015.html":
            depth += 1     # same deal as above but we only need to go one further down (to list of authors)
        elif self.url == "http://fieldnotes.makingandknowing.org/mainSpace/Field%20Notes%20Fall%202015.html" or self.url == "http://fieldnotes.makingandknowing.org/mainSpace/Field%20Notes%20-%20Spring%202016.html":
            text = text.partition("<br />")[0]      # stop parsing before links to other indexes
            
        if self.parent and (self.parent.url == "http://fieldnotes.makingandknowing.org/mainSpace/Fall%202014%20Archives.html" or self.parent.url == "http://fieldnotes.makingandknowing.org/mainSpace/Fall%202015%20Annotations.html"):
            return children     # if inside one of these folders, do not parse children (since the directory is flat; we will do this one manually)
            
        if depth == MAX_DEPTH:
            return children
        
        # /end edge cases
        
        links = REGEX[depth].findall(text)
        links = filter(lambda link: link[0][0]!="#" and not(any(bad in link[0] for bad in BAD_LIST)), links)
        
        for link in links:
            children.append(Node(link[URL], link[TITLE], self, depth+1))
            
        return children

    def get_html(self) -> str:
        if self.has_error:
            return None
        else:
            page = urllib.request.urlopen(self.url)            # open url
            return page.read().decode('utf-8')     # decode to text

from urllib.parse import quote, unquote
class Tree:
    
    def __init__(self, root):
        self.root = root
        
    def make_table(self, node):
        mapping = []
        if "\u0301" in node.old_path:
            print(node.old_path)
            node.old_path = node.old_path.encode('utf-8').decode('utf-8') #%CC%81%2C
            print(node.old_path)
            print(os.path.exists(node.old_path))
        if "\u0301" in node.new_path:
            print(node.new_path)  # this doesn't happen because sanitize(text) fixes it (downgrades to "e")
        # print((node.old_path.replace(ROOT_DIR + "/", ""), node.new_path.replace(ROOT_DIR + "/", "")))
        mapping.append((node.old_path.replace(ROOT_DIR + "/", ""), node.new_path.replace(ROOT_DIR + "/", "")))
        for child in node.children:
            mapping.extend(self.make_table(child))
        return mapping
    
    def make_graph(self, node):
        tree = "\n" + "\t"*node.depth + node.sanitize(node.title).lower()
        for child in node.children:
            tree += self.make_graph(child)
        return tree
    
    def find_errors(self, node):
        errors = []
        if node.has_error and ERROR_TABLE.get(node.old_url)==None:
            errors.append((node.parent.old_url, node.old_url))
            print("found error: " + node.old_url)
        for child in node.children:
            errors.extend(self.find_errors(child))
        return errors

def resolve_filename_conflict(path):
    '''
    Add a number onto the end of a duplicate filename to avoid conflicts
    '''
    old_path = path
    unique_identifier = 0
    while os.path.isfile(path):
        path = old_path
        unique_identifier += 1
        pair = os.path.splitext(path)
        path = pair[0] + " (" + str(unique_identifier) + ")" + pair[1]
    return path

def reorganize(mapping):
    '''
    Takes in a dict with original file paths mapping to new paths.
    '''
    missing = []
    for old_path, new_path in mapping.items():
        old_path = ROOT_DIR + "/" + old_path
        new_path = ROOT_DIR + "/" + new_path
        if os.path.exists(old_path):
            if os.path.exists(new_path):
                print("found duplicate: " + os.path.basename(new_path))
                new_path = resolve_filename_conflict(new_path)
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            os.rename(old_path, new_path)
        else:
            missing.append((old_path, new_path))
    return missing

# either do this before the initial move or after, not during.
# if we do it during it will duplicate files.
def update_hyperlinks(infile, mapping):
    with open(infile, mode="r") as f:
        text = f.read()
        links = re.findall(r'<a.*href="(.*)".*>', text)
        for link in links:
            i = text.find(link)
            if link in mapping:
                text = text[:i] + mapping[link] + text[i+len(link):]
            elif 'http' not in link and link[0]!='#':
                text = text[:i] + "/" + link + text[i+len(link):]   # "files/..." -> "/files/..."
    f.close()

    with open(infile, mode="w") as f:
        f.write(text)

if __name__=="__main__":

    with open(ERROR_TABLE_PATH, mode='r') as infile:
        reader = csv.reader(infile)
        ERROR_TABLE = {rows[1] : rows[2] for rows in reader}
        
    r = Node(SPACE_MENU, 'main', None, 0)
    t = Tree(r)
    graph = t.make_graph(t.root)
    table = t.make_table(t.root)
    # [print(k, ":", v) for k,v in table[10:20]]
    
    with open("fieldnotes/filetree.txt", mode='w') as outfile:
        outfile.write(graph)
    outfile.close()
    
    with open("fieldnotes/mapping.csv", mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        # writer.writerows([("original", "new")])
        writer.writerows(table)
    outfile.close()
    
    with open("fieldnotes/errors.csv", mode='a', newline='') as outfile:
        writer = csv.writer(outfile)
        # writer.writerows([("parent", "culprit")])
        writer.writerows(t.find_errors(t.root))
    outfile.close()
    
    mapping = {} 
    for t in table:
        mapping[t[0]] = t[1]        # the beauty of this solution is that it overwrites duplicates
        
    for infile in mapping.keys():
        update_hyperlinks(infile, mapping)
    
    missing = reorganize(mapping)
    with open("fieldnotes/missing.csv", mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        # writer.writerows([("missing file", "intended destination")])
        writer.writerows(missing)
    outfile.close()
        