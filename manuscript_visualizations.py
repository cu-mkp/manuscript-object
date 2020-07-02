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

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'


def tags_scatterplot(search_tags, filename, title):
    manuscript_version = "tl" # "tl", "tc" or "tcn"

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
    manuscript_version = "tl" # "tl", "tc" or "tcn"

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
    manuscript_version = "tl" # "tl", "tc" or "tcn"

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


def entry_words_scatterplot():
    for manuscript_version in ["tc", "tcn", "tl"]:

        entries = []
        lengths = []
        normalized_lengths = []
        folios = []

        for i in range(0, 340):
            number = format(i//2 + 1, '03')
            side = "r" if (i % 2 == 0) else "v"

            folio = f'{manuscript_version}_p{number}{side}_preTEI'
            #print(folio)
            input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

            tree = etree.parse(input_filename)

            for div in tree.findall(".//div"):
                entry = div.get("id")
                entry_text = etree.tostring(div, method = "text", encoding="UTF-8").decode('utf-8')
                entry_words = entry_text.split()
                number_of_words = len(entry_words)
                number_of_different_words = len(list(dict.fromkeys(entry_words))) # duplicates removed
                if entry in entries:
                    idx = entries.index(entry)
                    lengths[idx] += number_of_words
                    normalized_lengths[idx] += number_of_different_words
                else:
                    entries.append(entry)
                    lengths.append(number_of_words)
                    normalized_lengths.append(number_of_different_words)
                    folios.append(i//2 + 1)

        df = pandas.DataFrame({"entries": entries, "lengths": lengths, "normalized_lengths": normalized_lengths, "folio number": folios})

        plt.subplots(figsize = (10, 10))
        #plt.gcf().subplots_adjust(left = 0.05)
        #plt.gcf().subplots_adjust(right = 0.95)
        #points = plt.scatter(df["lengths"], df["normalized_lengths"], s = 0)
        #plt.colorbar(points)

        scatter = sns.scatterplot(x = "lengths", y = "normalized_lengths", hue = "folio number", data = df, linewidth = 0, alpha = 0.9)

        for line in range(0, df.shape[0]):
            if (df.lengths[line] > 1500):
                scatter.text(df.lengths[line] + 30, df.normalized_lengths[line], df.entries[line], horizontalalignment="left", fontsize = 10)

        scatter.set_ylabel("Number of different words", fontsize = 16)
        scatter.set_xlabel("Number of words", fontsize = 16)
        scatter.set_title(f"Lengths of entries [{manuscript_version}]", fontsize = 20)

        scatter.legend(fancybox = True)
        #scatter.set_yticklabels(scatter.get_yticklabels(), size = 16)

        fig = scatter.get_figure()
        fig.savefig(f"{viz_path}entry_words_scatterplot_{manuscript_version}.png")


def tags_by_category_swarmplot(search_tags, filename, title):
    manuscript_version = "tl" # "tl", "tc" or "tcn"

    entries = []
    entry_ids = []
    tags = []
    categories = []
    entry_count = 0

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
            category_list = div.get("categories")
            if isinstance(category_list, str):
                category_list = category_list.split(";")
            if category_list == None:
                continue
            id = entry_count
            if (entry not in entries):
                entry_count += 1

            for tag in search_tags:
                count = entry_text.count(f'<{tag}>')
                for j in range(int(count)):
                    for cat in category_list:
                        entries.append(entry)
                        entry_ids.append(id)
                        tags.append(tag)
                        categories.append(cat)

    df = pandas.DataFrame({"entries": entries, "tags": tags, "entry_ids": entry_ids, "categories": categories})

    plt.subplots(figsize = (21, 15))
    plt.gcf().subplots_adjust(right = 0.99)

    swarm = sns.swarmplot(x = "entry_ids", y = "categories", hue = "tags", dodge = True, data = df, size = 3)

    swarm.grid(False)
    swarm.set_ylabel("Categories", fontsize = 20)
    swarm.set_xlabel("Entries", fontsize = 20)
    swarm.set_title(title, fontsize = 24)

    swarm.set_xticklabels([])
    swarm.set_yticklabels(swarm.get_yticklabels(), fontsize = 12)
    swarm.legend(fancybox = True)

    fig = swarm.get_figure()
    fig.savefig(f"{viz_path}{filename}.png")


viz_path = f'{m_path}/manuscript-object/manuscript_visualizations/'

if not os.path.exists(viz_path):
    os.mkdir(viz_path)

language_tags = ["fr", "el", "it", "la", "oc", "po"]

title = "Other languages in the English translation of the manuscript"
tags_scatterplot(language_tags, "languages_scatterplot", title)

tags_bubbleplot(language_tags, "languages_bubbles", "Other languages in the English translation of the manuscript", False)
tags_bubbleplot(language_tags, "languages_bubbles_normalized", "Other languages in the English translation of the manuscript (normalized by entry length)", True)

tags_bubbleplot(["del", "add"], "add_del_bubbles", "Additions and deletions by the author-practitioner", False)
tags_bubbleplot(["del", "add"], "add_del_bubbles_normalized", "Additions and deletions by the author-practitioner (normalized by entry length)", True)

categories_barplot()

entry_words_scatterplot()

tags_by_category_swarmplot(["del", "add"], "add_del_swarmplot", "Additions and deletions by the author-practitioner")

print("All done!")
