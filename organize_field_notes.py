import os
import re
from url_to_html import url_to_html, HTTPError
import csv

# Variables
mainSpace = 'http://fieldnotes.makingandknowing.org/mainSpace'
space_menu = f'{mainSpace}/space.menu.html'

URL = 0        # url is first in regex Match tuple
TITLE = 1      # title is second in regex Match tuple

semesters_header = 'Course Archives'
re_semesters = re.compile(r'<li><a.*?href="(.*?)".*?>(.*?)</a></li>') # get url of each semester
re_intermediate = re.compile(r'<a.*?href="(.*?)".*?>(.*Field Notes.*)</a>') # get url of intermediate field notes folder for a given semester
re_authors = re.compile(r'<a.*?href="(.*?)".*?>(.*?)</a>') # get url of each author for a given semester
re_fieldnotes = re.compile(r'<a.*?href="(.*?)".*?>(.*?)</a>') # get url of each field note for a given author

# Functions

def make_url(url:str) -> str:
    """
    Replace all spaces in a string with dashes in order to make it a viable url.
    """
    return url.replace(" ", "-")

def make_tree():
    tree = ""
    table = []
    depth = 0

    newpath = mainSpace
    menu_html = url_to_html(space_menu)

    semesters = re_semesters.findall(menu_html[menu_html.find(semesters_header):]) # get list of semesters after semesters section header

    for semester in semesters:
        newpath += f'/{semester[TITLE]}'
        try:
            semester_html = url_to_html(f'{mainSpace}/{semester[URL]}') # get html of semester page
        except HTTPError:
            print("URL not found: " + semester[URL])
            newpath = newpath[:len(newpath) - len(semester[TITLE]) - 1]
            continue
        
        # collapse the intermediate page
        intermediate = re_intermediate.findall(semester_html)[0] # get the intermediate page linking to the list of authors
        try:
            intermediate_html = url_to_html(f'{mainSpace}/{intermediate[URL]}')
        except HTTPError:
            print("URL not found: " + intermediate[URL])
            newpath = newpath[:len(newpath) - len(semester[TITLE]) - 1]
            continue
        
        authors = re_authors.findall(intermediate_html) # get list of authors
        
        tree += "\n" + "blah"*depth + semester[TITLE]
        
        depth += 1
        for author in authors:
            newpath += f'/{author[TITLE]}'
            try:
                author_html = url_to_html(f'{mainSpace}/{author[URL]}')
            except HTTPError:
                print("URL not found: " + author[URL])
                newpath = newpath[:len(newpath) - len(author[TITLE]) - 1]
                continue
            
            fieldnotes = re_fieldnotes.findall(author_html) # get list of fieldnotes
            
            tree += "\n" + "\t"*depth + author[TITLE]
            
            depth += 1
            for fieldnote in fieldnotes:
                newpath += f'/{fieldnote[TITLE]}'
                # add paths
                tree += "\n" + "\t"*depth + fieldnote[TITLE]
                table.append((f'{mainSpace}/{fieldnote[URL]}', make_url(newpath)))
                
                # step back
                newpath = newpath[:len(newpath) - len(fieldnote[TITLE]) - 1]
            
            depth -= 1
            
            # step back
            newpath = newpath[:len(newpath) - len(author[TITLE]) - 1]
        
        depth -= 1
        
        # step back=
        newpath = newpath[:len(newpath) - len(semester[TITLE]) - 1]
    
    return (table, tree)

def organize_field_notes(write=True):
    table, tree = make_tree()
    if write:
        with open("fieldnotes/filetree.txt", "w") as f:
            f.write(tree)
        
        with open("fieldnotes/filetable.csv", "w") as f:
            writer = csv.writer(f)
            writer.writerows(table)

if __name__=="__main__":
    organize_field_notes()