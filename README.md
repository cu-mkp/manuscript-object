# manuscript-object

The BnF() Class represents a python version of BnF Ms 640. A static object within this class `complete_manuscript` contains every entry. Any other instantiation of the class holds a subset of these entries. 

Entries have their own class, Recipe(), which formats each entry and parses out specific features. 

When BnF() is defined, `complete_manuscript` is instantiated, which calls a function in `manuscript helpers` to generate the complete manuscript. The manuscript object, which is positioned in the same directory as the manuscript data, opens each file in `/ms-xml/` for each version, and conscripts an entry object with it. These entry objects are held in a list called `entries`, and sorted.

# Dana's work

The files I worked with are Elmo_contextual_embeddings.ipynb, vocabulary_abstraction.ipynb and word_clouds.py.
they require python packages, respectively numpy pandas tensorflow tensorflow_hub scikit-learn spacy ipython chart_studio, pandas nltk print-tree2 and wordcloud.

Elmo is a machine learning model who uses context to try and find semantic similarities between sentences. It is very memory heavy. In my notebook, I feed it the whole manuscript or some categories of entries. The results are in Sentence_encode, they are html files so they will open in a browser.

Vocabulary abstraction creates a semantic tree with all the single words from a category in the thesaurus. It uses the wordnet dictionnary which allows us to access hypernyms. All the outputs are directly in the notebook.

word_clouds makes wordclouds for every category of tagged terms from the thesaurus. The outputs are in word_clouds

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
Then, `cd manuscript object`

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
