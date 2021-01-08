# Last Updated | 2021-01-07
# Python Modules
import os
import sys
from typing import List, Dict
import json
import argparse

# Third Party Modules
from datetime import datetime

# Local Modules
import manuscript
import utils

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
    """Generate the entire manuscript and write all derivative files, by default.
    Various command line arguments permit alternative actions, as described by each one's help message.
    """
    parser = argparse.ArgumentParser(description="Generate and update derivative files from original ms-xml folios.")
    parser.add_argument('-d', '--dry-run', help="Generate as usual, but do not write derivatives.", action="store_true")
    parser.add_argument('-v', '--verbose', help="Write verbose generation progress to stdout.", action="store_true")
    parser.add_argument('-b', '--bypass', help="Bypass user y/n confirmation. Useful for automation.", action="store_true")
    parser.add_argument('-a', '--all-folios', nargs="?", default=argparse.SUPPRESS, const=utils.all_folios_path, help="Update allFolios derivative files. Disables generation of other derivatives unless those are also specified. Optional argument: folder path to which to write derivative files.")
    parser.add_argument('-m', '--metadata', nargs="?", default=argparse.SUPPRESS, const=utils.metadata_path, help="Update metadata derivative files. Disables generation of other derivatives unless those are also specified. Optional argument: folder path to which to write derivative files.")
    parser.add_argument('-t', '--txt', nargs="?", default=argparse.SUPPRESS, const=utils.ms_txt_path, help="Update ms-txt derivative files. Disables generation of other derivatives unless those are also specified. Optional argument: folder path to which to write derivative files.")
    parser.add_argument('-e', '--entries', nargs="?", default=argparse.SUPPRESS, const=utils.entries_path, help="Update entries derivative files. Disables generation of other derivatives unless those are also specified. Optional argument: folder path to which to write derivative files.")
    parser.add_argument("path", nargs="?", default=utils.manuscript_data_path, help="Path to m-k-manuscript-data directory. Defaults to the sibling of your current directory.")

    args = parser.parse_args()

    # Verify that manuscript-data path exists.
    assert(os.path.exists(args.path)), ("Could not find manuscript data directory: " + args.path)
    assert(os.path.exists(args.path + "/ms-xml")), ("Could not find ms-xml folder in manuscript data directory: " + args.path + "/ms-xml")

    if not args.bypass:
        okay = input(f"Using manuscript data path: {args.path}. Confirm (Y/n)? ").lower() in ("", "y", "yes")
        if not okay:
            return

    if not args.verbose:
        sys.stdout = open(os.devnull, "w") # Turn off print statements by sending them to /dev/null. Is this a bad idea? I need a UNIX expert.

    # If no specific derivatives were specified, generate all of them.
    if not any(flag in args for flag in ('all_folios', 'entries', 'txt', 'metadata')):
        args.all_folios = utils.all_folios_path
        args.entries = utils.entries_path
        args.txt = utils.ms_txt_path
        args.metadata = utils.metadata_path

    dirs = [os.path.join(args.path, "ms-xml", v) for v in utils.versions]
    ms = manuscript.Manuscript.from_dirs(*dirs)

    # Write only the derivatives specified.
    if 'metadata' in args:
        if not args.dry_run:
            print('Updating metadata..', file=sys.__stdout__)
        ms.update_metadata(outdir=args.metadata, dry_run=args.dry_run)

    if 'entries' in args:
        if not args.dry_run:
            print('Updating entries...', file=sys.__stdout__)
        ms.update_entries(outdir=args.entries, dry_run=args.dry_run)

    if 'txt' in args:
        if not args.dry_run:
            print('Updating ms-txt...', file=sys.__stdout__)
        ms.update_ms_txt(outdir=args.txt, dry_run=args.dry_run)

    if 'all_folios' in args:
        if not args.dry_run:
            print('Updating allFolios...', file=sys.__stdout__)
        ms.update_all_folios(outdir=args.all_folios, dry_run=args.dry_run)

    update_time()

if __name__ == "__main__":
    update()
