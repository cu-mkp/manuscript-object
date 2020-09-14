# manuscript-object

The `BnF` class represents a python version of BnF Ms 640. It contains a list of `Recipe` objects, which hold the raw XML data from each entry along with some other data such as length and properties.

When `BnF` is instantiated, it loads every folio in [`ms-xml`](https://github.com/cu-mkp/m-k-manuscript-data/tree/master/ms-xml) and processes it into its component entries, each of which becomes a `Recipe` object.

`update.py` is a script that generates the `BnF` object and then writes derivative forms and the entry-metadata table to the [m-k-manuscript-data repository](https://github.com/cu-mkp/m-k-manuscript-data).

The derivative files/folders are:
- allFolios/: for each version, a single XML file containing each folio concatenated together
- entries/: for each version, every entry as a single file in both XML and TXT formats
- metadata/entry-metadata.csv: listing of the properties of each entry, including IDs, headings, and semantic tags (the significant properties of the manuscript as defined by the M&K Project editors), which is used to generate the ["List of Entries"](https://edition640.makingandknowing.org/#/entries) page on the [edition640.makingandknowing.org](https://edition640.makingandknowing.org/#/) website
- ms-txt/: for each version, every folio as a single file in TXT format

Note for TXT versions:
- utf-8 encoding
- ampersand (&) is rendered in its literal form rather than the character entity `&amp;`
- text marked as `<add>` (additions), `<corr>` (corrections), `<del>` (deletions), `<exp>` (expansions), or `<sup>` (supplied) in the XML files under ms-xml is retained
- figures and comments are absent and unmarked

# Running update.py
```
usage: update.py [-h] [-d] [-s] [-b] [-c] [-q] [-a] [-m] [-t] [-e] [path]

Generate derivative files from original ms-xml folios.

positional arguments:
  path              Path to m-k-manuscript-data directory. Defaults to the sibling of your current directory.

optional arguments:
  -h, --help        show this help message and exit
  -d, --dry-run     Generate as usual, but do not write derivatives.
  -s, --silent      Silence output. Do not write generation progress to terminal.
  -b, --bypass      Bypass user y/n confirmation. Useful for automation.
  -c, --cache       Save manuscript object to a JSON cache for quicker loading next time.
  -q, --quick       Use JSON cache of manuscript object to speed up generation process. Don't do this if you need to
                    include changes from ms-xml!
  -a, --all-folios  Generate allFolios derivative files. Disables generation of other derivatives unless those are
                    also specified.
  -m, --metadata    Generate metadata derivative files. Disables generation of other derivatives unless those are also
                    specified.
  -t, --txt         Generate ms-txt derivative files. Disables generation of other derivatives unless those are also
                    specified.
  -e, --entries     Generate entries derivative files. Disables generation of other derivatives unless those are also
                    specified.
```

# Setup
Note: if you have multiple versions of Python 3 installed, specify that version when running bash commands. E.g. `python3.7` instead of `python3`.

1. Install [Python](https://www.python.org/) (version 3.7+)

2. Install [Pip](https://pypi.org/project/pip/)

3. Install [Pipenv](https://pypi.org/project/pipenv/) via `python3 -m pip3 install pipenv`

4. Clone the repositories into separate folders in the same directory: 
```bash
git clone https://github.com/cu-mkp/m-k-manuscript-data
git clone https://github.com/cu-mkp/manuscript-object
```
E.g. after running these commands in a folder called 'mkp', you should see:
```
mkp/
  m-k-manuscript-data/
    ...
  manuscript-object/
    ...
```

5. Run `python3 -m pipenv install` to install dependencies to the pipenv shell.

6. To enter the pipenv shell, run `python3 -m pipenv shell`. To exit, press ^D or type `exit`. Inside the pipenv shell, all outside dependencies for the repository are installed.
