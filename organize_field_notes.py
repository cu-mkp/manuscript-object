import os
import re
import urllib.request
import urllib.error
import urllib.parse
import csv

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

class Node:

    def __init__(self, url, title, parent, depth):
        # print("parent: " + str(parent))
        # print("depth: " + str(depth))
        self.old_url = URL_PREFIX + "/" + url   # this is for making the final table; remains unchanged
        self.url = URL_PREFIX + "/" + url       # this is for working with the file; can be changed
        self.title = title
        self.parent = parent
        self.depth = depth
        self.hasError = self.checkError(self.url)
        if self.hasError:
            self.hasError = not self.repairUrl()
        self.old_path = ROOT_DIR + urllib.parse.unquote(self.url)[len(URL_PREFIX):]    # I am somewhat ashamed of this code.
        self.new_path = self.makeNewPath()
        print(self.old_path[len(ROOT_DIR):] + " -> " + self.new_path[len(ROOT_DIR):])
        self.children = self.findChildren()
        
    def checkError(self, url) -> bool:
        '''
        True -> url causes HTTP error
        False -> url is fine
        '''
        try:
            urllib.request.urlopen(url)
        except urllib.error.HTTPError:
            return True
        return False
    
    def repairUrl(self) -> bool:
        '''
        Returns Boolean to indicate success of repairing url.
        !! This method modifies self.url !!!
        '''
        correction = ERROR_TABLE.get(self.old_url)
        if correction == None:
            return False
        elif correction != "?" and correction != "":
            self.url = correction
            print(self.old_url + " corrected to " + correction)
            return not self.checkError(self.url)
        else:
            return False
            
    def makeNewPath(self) -> str:
        if self.parent:
            parent_directory = os.path.dirname(self.parent.new_path)
        else:
            parent_directory = os.path.dirname(ROOT_DIR)  # should resolve to "C:/Users/grsch/Desktop"
        return parent_directory + "/" + self.sanitize(self.title).lower() + '/index.html'*(self.depth!=MAX_DEPTH) + '.html'*(self.depth==MAX_DEPTH)
    
    def sanitize(self, text):
        if self.old_url == "http://fieldnotes.makingandknowing.org/mainSpace/Field%20Notes%20-%20Spring%202016.html":
            tmp = text.partition(',')
            text = tmp[2] + " " + tmp[0]     # fix "LastName, FirstName" situations (maybe)
            
        disallowed = ['.', ':', ',', ';', '/', '\\', '\'', '"', '#', '<', '>', '|', '*', '?']      # remove these invalid symbols
        for symbol in disallowed:
            text = text.replace(symbol, '')
        
        return text.replace(' - ', '_').replace(' ', '-').replace('%20', '-').replace('&amp', '+').replace('&', '+')
    
    def findChildren(self):
        children = []
        depth = self.depth   # We have to define this separately for stupid edge-case reasons. :(
        
        if self.hasError:
            return children
        
        text = self.getHtml()
        
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

    def getHtml(self) -> str:
        if self.hasError:
            return None
        else:
            page = urllib.request.urlopen(self.url)            # open url
            return page.read().decode('utf-8')     # decode to text
        
class Tree:
    
    def __init__(self, root):
        self.root = root
        
    def makeTable(self, node):
        mapping = []
        mapping.append((node.old_path, node.new_path))
        for child in node.children:
            mapping.extend(self.makeTable(child))
        return mapping
    
    def makeGraph(self, node):
        tree = "\n" + "\t"*node.depth + node.sanitize(node.title).lower()
        for child in node.children:
            tree += self.makeGraph(child)
        return tree
    
    def findErrors(self, node):
        errors = []
        if node.hasError and ERROR_TABLE.get(node.old_url)==None:
            errors.append((node.parent.old_url, node.old_url))
        for child in node.children:
            errors.extend(self.findErrors(child))
        return errors

def reorganize(mapping):
    '''
    Takes in a dict with original file paths mapping to new paths.
    '''
    for old_path, new_path in mapping.items():
        if os.path.isfile(old_path):
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            os.rename(old_path, new_path)

if __name__=="__main__":

    with open(ERROR_TABLE_PATH, mode='r') as infile:
        reader = csv.reader(infile)
        ERROR_TABLE = {rows[1] : rows[2] for rows in reader}
        
    r = Node(SPACE_MENU, 'main', None, 0)
    t = Tree(r)
    graph = t.makeGraph(t.root)
    table = t.makeTable(t.root)
    
    with open("fieldnotes/newtree.txt", mode='w') as outfile:
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
        writer.writerows(t.findErrors(t.root))
    outfile.close()
    
    mapping = {} 
    for t in table:
        mapping[t[0]] = t[1]        # the beauty of this solution is that it overwrites duplicates
        
    reorganize(mapping)