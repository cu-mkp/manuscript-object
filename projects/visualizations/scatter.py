import matplotlib.pyplot as plt
from manuscript import *

m = Manuscript(utils.ms_xml_path)

ids = []
n_terms = []
for id, entry in m.entries["tl"].items():
    terms = find_terms(entry.xml, "env")
    if len(terms) > 0:
        ids.append(id)
        n_terms.append(len(terms))

plt.xlabel("Entry ID")
plt.ylabel("# env tags")
plt.xticks(range(0,len(ids),10), ids[::10], rotation=70, fontsize="x-small")
plt.yticks(range(0,max(n_terms)+1))
plt.scatter(ids, n_terms)
for i, id in enumerate(ids):
    if n_terms[i] > 4:
        plt.annotate(id, (ids[i], n_terms[i]), rotation=30, fontsize="x-small")

plt.show()
save = input("Save fig? (Y/n)")
if save == "" or save.lower() in ("y", "yes"):
    plt.savefig("scatter.png")
