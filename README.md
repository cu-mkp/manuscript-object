# manuscript-object

The BnF() Class represents a python version of BnF Ms 640. A static object within this class `complete_manuscript` contains every manuscript. Any other instantiation of the class holds a subset of these entries. 

Entries have their own class, Recipe(), which formats each entry and parses out specific features. 

When BnF() is defined, `complete_manuscript` is instantiated, which calls a function in `manuscript helpers` to generate the complete manuscript. The manuscript object, which is positioned in the same directory as the manuscript data, opens each file in `/ms-xml/` for each version, and conscripts an entry object with it. These entry objects are held in a list called `entries`, and sorted.

# Setup
Have python installed on your machine.
Put `m-k-manuscript-data` and `manuscript-object` in the same directory.