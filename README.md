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

