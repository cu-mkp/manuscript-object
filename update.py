# Last Updated | 2020-10-22
# Python Modules
import os
import sys
from typing import List, Dict
import json
import argparse

# Third Party Modules
from datetime import datetime

# Local Modules
from manuscript import Manuscript
from utils import manuscript_data_path, versions, prop_dict

def update_time():
    """ Extract timestamp at the top of this file and update it. """
    # Initialize date to write and container for the text
    now_str = str(datetime.now()).split(' ')[0]
    lines = []

    # open file, extract text, and modify
    with open('./update.py', 'r') as f:
        lines = f.read().split('\n')

    lines[0] = f'# Last Updated | {now_str}'

    # write modified text
    with open('./update.py', 'w') as f:
        f.write('\n'.join(lines))

def update():
    parser = argparse.ArgumentParser(description="Generate derivative files from original ms-xml folios.")
    parser.add_argument('-d', '--dry-run', help="Generate as usual, but do not write derivatives.", action="store_true")
    parser.add_argument('-s', '--silent', help="Silence output. Do not write generation progress to terminal.", action="store_true")
    parser.add_argument('-b', '--bypass', help="Bypass user y/n confirmation. Useful for automation.", action="store_true")
    parser.add_argument('-a', '--all-folios', help="Generate allFolios derivative files. Disables generation of other derivatives unless those are also specified.", action="store_true")
    parser.add_argument('-m', '--metadata', help="Generate metadata derivative files. Disables generation of other derivatives unless those are also specified.", action="store_true")
    parser.add_argument('-t', '--txt', help="Generate ms-txt derivative files. Disables generation of other derivatives unless those are also specified.", action="store_true")
    parser.add_argument('-e', '--entries', help="Generate entries derivative files. Disables generation of other derivatives unless those are also specified.", action="store_true")
    parser.add_argument("path", nargs="?", action="store", default=manuscript_data_path, help="Path to m-k-manuscript-data directory. Defaults to the sibling of your current directory.")

    options = parser.parse_args()


    # verify manuscript-data path
    assert(os.path.exists(options.path)), ("Could not find manuscript data directory: " + options.path)
    assert(os.path.exists(options.path + "/ms-xml")), ("Could not find ms-xml folder in manuscript data directory: " + options.path + "/ms-xml")

    if not options.bypass:
        okay = input(f"Using manuscript data path: {options.path}. Confirm (Y/n)? ").lower() in ("", "y", "yes")
        if not okay:
          return

    if options.silent:
        sys.stdout = open(os.devnull, "w") # turn off print statements. Is this a bad idea?

    # if no specific derivatives were specified, generate all of them
    if not any([options.all_folios, options.metadata, options.txt, options.entries]):
        generate_all_derivatives = True
    else:
        generate_all_derivatives = False

    manuscript = Manuscript(os.path.join(options.path, "ms-xml"))

    if not options.dry_run:
        if options.metadata or generate_all_derivatives:
            print('Updating metadata..', file=sys.__stdout__)
            manuscript.update_metadata()

        if options.entries or generate_all_derivatives:
            print('Updating entries...', file=sys.__stdout__)
            manuscript.update_entries()

        if options.txt or generate_all_derivatives:
            print('Updating ms-txt...', file=sys.__stdout__)
            manuscript.update_ms_txt()

        if options.all_folios or generate_all_derivatives:
            print('Updating allFolios...', file=sys.__stdout__)
            manuscript.update_all_folios()

    update_time()

if __name__ == "__main__":
    update()
