""" Data visualizations of the manuscript. """
# Python Modules
import csv
import os

# Third-Party Modules
from lxml import etree
import numpy as np
import pandas
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt

manuscript_version = "tl" # "tl", "tc" or "tcn"

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'


def tags_scatterplot(search_tags, filename, title):
    folios = []
    tags = []
    counts = []

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = f'{manuscript_version}_p{number}{side}_preTEI'
        #print(folio)
        input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

        tree = etree.parse(input_filename)

        for tag in search_tags:
            folio_text = etree.tostring(tree, method = "xml", encoding="UTF-8").decode('utf-8')
            folios.append(number+side)
            tags.append(tag)
            counts.append(folio_text.count(f'<{tag}>'))

    df = pandas.DataFrame({"folios": folios, "tags": tags, "counts": counts})

    plt.subplots(figsize = (20, 10))
    plt.gcf().subplots_adjust(left = 0.05)
    plt.gcf().subplots_adjust(right = 0.95)
    scatter = sns.scatterplot(x = "folios", y = "counts", hue = "tags", data = df)

    scatter.set_ylabel("Tag count", fontsize = 20)
    scatter.set_xlabel("Folios", fontsize = 20)
    scatter.set_title(title, fontsize = 24)
    scatter.set_xticklabels(folios, rotation = 90, fontsize = 4)
    #scatter.set_yticklabels(scatter.get_yticklabels(), size = 16)

    fig = scatter.get_figure()
    fig.savefig(f"{viz_path}{filename}.png")


def tags_bubbleplot(search_tags, filename, title, normalized):
    entries = []
    tags = []
    counts = []

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = f'{manuscript_version}_p{number}{side}_preTEI'
        #print(folio)
        input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

        tree = etree.parse(input_filename)

        for div in tree.findall(".//div"):
            entry = div.get("id")
            entry_text = etree.tostring(div, method = "xml", encoding="UTF-8").decode('utf-8')

            for tag in search_tags:
                entries.append(entry)
                tags.append(tag)
                count = entry_text.count(f'<{tag}>')
                if normalized:
                    pure_text = etree.tostring(div, method = "text", encoding="UTF-8").decode('utf-8')
                    entry_length = len(pure_text.split())
                    if entry_length != 0:
                        count /= entry_length
                counts.append(count)

    df = pandas.DataFrame({"entries": entries, "tags": tags, "counts": counts})

    plt.subplots(figsize = (15, 5))
    #plt.gcf().subplots_adjust(left = 0.05)
    #plt.gcf().subplots_adjust(right = 0.95)
    bubbleplot = sns.scatterplot(x = "entries", y = "tags", size = "counts", sizes = (10, 500), data = df, linewidth = 0, alpha = 0.3)

    bubbleplot.grid(False)
    bubbleplot.set_ylabel("Tags", fontsize = 16)
    bubbleplot.set_xlabel("Entries", fontsize = 16)
    bubbleplot.set_title(title, fontsize = 20)

    bubbleplot.set_xticklabels([], rotation = 90, fontsize = 6)
    bubbleplot.legend(fancybox = True)
    #scatter.set_yticklabels(scatter.get_yticklabels(), size = 16)

    fig = bubbleplot.get_figure()
    fig.savefig(f"{viz_path}{filename}.png")


def categories_barplot():
    categories = ["casting", "painting", "metal process", "varnish",
                  "arms and armor", "medicine", "household and daily life",
                  "cultivation", "stones", "wood and its coloring", "tool",
                  "tricks and sleight of hand", "decorative",
                  "animal husbandry", "glass process", "corrosives", "dyeing",
                  "preserving", "wax process", "practical optics", "lists",
                  "merchants", "printing", "La boutique", "alchemy",
                  "manuscript structure"]
    counts = np.zeros(len(categories))

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = f'{manuscript_version}_p{number}{side}_preTEI'
        #print(folio)
        input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

        tree = etree.parse(input_filename)

        for div in tree.findall(".//div"):
            category_list = div.get("categories")
            if category_list != None:
                category_list = category_list.split(";")
                for i in range(len(categories)):
                    if categories[i] in category_list:
                        counts[i] += 1

    df = pandas.DataFrame({"counts": counts, "categories": categories})
    cat_order = df.sort_values("counts", ascending = False).categories

    plt.subplots(figsize = (10, 10))
    plt.gcf().subplots_adjust(bottom = 0.35)
    barplt = sns.barplot(x = "categories", y = "counts", data = df,
                         order = cat_order)

    total_sum = sum(counts)
    print(total_sum)
    for p in barplt.patches:
        nb = format(p.get_height()/total_sum*100, '.2f')
        barplt.annotate(nb + "%", (p.get_x() + p.get_width(), p.get_height() + 5),
                        ha = 'center', va = 'center', xytext = (0, 10),
                        textcoords = 'offset points', rotation = 45)

    barplt.set_ylabel("Number of entries", fontsize = 18)
    barplt.set_xlabel("Categories", fontsize = 18)
    barplt.set_title("How many entries there are for each category", fontsize = 20)

    barplt.set_xticklabels(barplt.get_xticklabels(), rotation = 90, fontsize = 16)
    #scatter.set_yticklabels(scatter.get_yticklabels(), size = 16)
    fig = barplt.get_figure()
    fig.savefig(viz_path + "categories_barplot.png")



viz_path = f'{m_path}/manuscript-object/manuscript_visualizations/'

if not os.path.exists(viz_path):
    os.mkdir(viz_path)

language_tags = ["fr", "el", "it", "la", "oc", "po"]

title = "Other languages in the English translation of the manuscript"
tags_scatterplot(language_tags, "languages_scatterplot", title)

tags_bubbleplot(language_tags, "languages_bubbles", "Other languages in the English translation of the manuscript", False)
tags_bubbleplot(language_tags, "languages_bubbles_normalized", "Other languages in the English translation of the manuscript (normalized by entry length)", True)

tags_bubbleplot(["del", "add"], "modifications_bubbles", "Additions and deletions by the author-practitioner", False)
tags_bubbleplot(["del", "add"], "modifications_bubbles_normalized", "Additions and deletions by the author-practitioner (normalized by entry length)", True)

categories_barplot()

print("All done!")
