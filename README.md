# manuscript-object

The BnF() Class represents a python version of BnF Ms 640. A static object within this class `complete_manuscript` contains every manuscript. Any other instantiation of the class holds a subset of these entries. 

Entries have their own class, Recipe(), which formats each entry and parses out specific features. 

When BnF() is defined, `complete_manuscript` is instantiated, which calls a function in `manuscript helpers` to generate the complete manuscript. The manuscript object, which is positioned in the same directory as the manuscript data, opens each file in `/ms-xml/` for each version, and conscripts an entry object with it. These entry objects are held in a list called `entries`, and sorted.

# Setup

1. If you do not have python3 downloaded on your machine, download it with brew. 

```bash
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew doctor
```

If brew is already installed, make sure it is up to date:
```bash
brew update     #Updates homebrew and recipes
brew upgrade    #Updates packages
```

Then run,
```bash
brew install python3 git pipenv
```

2. Run 
```bash
git clone git@github.com:cu-mkp/m-k-manuscript-data.git
git clone git@github.com:cu-mkp/manuscript-object.git
```
Then, `cd manuscript-object`

3. Run `pipenv install` to install dependencies to the pipenv shell.

4. To enter the pipenv shell, run `pipenv shell`. To exit, press ^D or type `exit`. Inside the pipenv shell, all outside dependencies for the repository are installed. 

# Setup for Windows

1. If you do not have python3 downloaded on you machine, I would advise you install Anaconda. It will make it easier for us to install the necessary packages. Go to https://www.anaconda.com/products/individual, scroll to the bottom of the page and download the proper installer for your computer then run it (we want python 3.7).

2. If you do not have it, install git.

3. Open the Windows PowerShell, use cd to go where you want the project to be, then run 
```bash
git clone git@github.com:cu-mkp/m-k-manuscript-data.git
git clone git@github.com:cu-mkp/manuscript-object.git
```

4. We need to install all necessary python packages, in anaconda powershell prompt run :
```bash
conda install pandas nltk pip
pip install print-tree2
pip install spacy
pip install wordcloud
```

5. We now need to run our notebooks. In anaconda powershell prompt, use cd to navigate to the folder where you copied the manuscript object. Then run `jupyter notebook`. In Jupyter you can now open the notebooks and run them.

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
