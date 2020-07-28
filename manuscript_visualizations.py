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
import matplotlib.ticker as ticker

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'

all_categories = ["casting", "painting", "metal process", "arms and armor",
                  "varnish", "medicine", "household and daily life",
                  "cultivation", "stones", "wood and its coloring", "tool",
                  "tricks and sleight of hand", "animal husbandry",
                  "decorative", "glass process", "corrosives", "dyeing",
                  "preserving", "wax process", "practical optics", "lists",
                  "merchants", "printing", "La boutique", "alchemy",
                  "manuscript structure"]


# cleans the tag string by remove some characters
def clean_tag(str):
    remove_chars = ["<", ">", "/"]
    for c in remove_chars:
        str = str.replace(c, "")
    return str


def tags_scatterplot(search_tags, filename, title):
    manuscript_version = "tl" # "tl", "tc" or "tcn"

    folios = []
    tags = []
    counts = []

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = f'{manuscript_version}_p{number}{side}_preTEI'
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
    plt.close()


def tags_bubbleplot(search_tags, ylabels, filename, title):
    manuscript_version = "tl" # "tl", "tc" or "tcn"

    entries = []
    tags = []
    counts = []
    normalized_counts = []

    entry = None

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = f'{manuscript_version}_p{number}{side}_preTEI'
        input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

        tree = etree.parse(input_filename)

        for div in tree.findall(".//div"):
            new_entry = div.get("id")
            if new_entry != None:
                entry = new_entry
            if entry == None:
                continue

            entry_text = etree.tostring(div, method = "xml", encoding="UTF-8").decode('utf-8')

            for tag in search_tags:
                entries.append(entry)
                tags.append(clean_tag(tag))
                count = entry_text.count(clean_tag(tag))
                counts.append(count)

                pure_text = etree.tostring(div, method = "text", encoding="UTF-8").decode('utf-8')
                entry_length = len(pure_text.split())
                normalized_count = count
                if entry_length != 0:
                    normalized_count /= entry_length
                normalized_counts.append(normalized_count)

    df = pandas.DataFrame({"entries": entries, "tags": tags, "counts": counts})
    df_normalized = pandas.DataFrame({"entries": entries, "tags": tags,
                                      "counts": normalized_counts})

    data_frames = [df, df_normalized]
    title_appendices = ["", " (normalized by entry length)"]
    filename_apppendices = ["", "_normalized"]

    for i in range(2):

        plt.subplots(figsize = (15, 5))
        plt.gcf().subplots_adjust(bottom = 0.2)
        plt.gcf().subplots_adjust(left = 0.15)
        bubbleplot = sns.scatterplot(x = "entries", y = "tags", size = "counts",
                                     sizes = (0, 500), data = data_frames[i],
                                     linewidth = 0, alpha = 0.3)

        bubbleplot.grid(False)
        bubbleplot.set_ylabel("Tags", fontsize = 16)
        bubbleplot.set_xlabel("Entries", fontsize = 16)
        bubbleplot.set_title(title + title_appendices[i], fontsize = 20)

        individual_entries = list(dict.fromkeys(entries))
        xlabels = []
        for j in range(len(individual_entries)):
            if j % 25 == 0:
                xlabels.append(individual_entries[j])
            else:
                xlabels.append("")
        bubbleplot.set_xticklabels(xlabels, rotation = 90, fontsize = 6)
        bubbleplot.set_yticklabels(ylabels, fontsize = 12)
        #bubbleplot.legend(loc = "best", ncol = 1, framealpha = 0.2, fancybox = True)
        plt.legend(bbox_to_anchor = (1.03, 0.5), loc = "center left",
                   fancybox = True)

        fig = bubbleplot.get_figure()
        fig.savefig(f"{viz_path}{filename}{filename_apppendices[i]}.png")
        plt.close()


def categories_barplot():
    manuscript_version = "tl" # "tl", "tc" or "tcn"

    counts = np.zeros(len(all_categories))
    entries = []

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = f'{manuscript_version}_p{number}{side}_preTEI'
        input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

        tree = etree.parse(input_filename)

        for div in tree.findall(".//div"):
            entry = div.get("id")
            if entry == None or entry in entries:
                # has already been seen or is not an entry
                continue
            entries.append(entry)
            category_list = div.get("categories")
            if category_list != None:
                category_list = category_list.split(";")
                for i in range(len(all_categories)):
                    if all_categories[i] in category_list:
                        counts[i] += 1
    df = pandas.DataFrame({"counts": counts, "categories": all_categories})
    cat_order = df.sort_values("counts", ascending = False).categories

    plt.subplots(figsize = (10, 10))
    plt.gcf().subplots_adjust(bottom = 0.35)
    barplt = sns.barplot(x = "categories", y = "counts", data = df,
                         order = cat_order, palette = "deep")

    total_sum = sum(counts)
    for p in barplt.patches:
        nb = format(p.get_height()/total_sum*100, '.2f')
        barplt.annotate(nb + "%", (p.get_x() + p.get_width()/2, p.get_height()),
                        ha = 'center', va = 'center', xytext = (0, 25),
                        textcoords = 'offset points', rotation = 90)

    barplt.set_ylabel("Number of entries", fontsize = 18)
    barplt.set_xlabel("Categories", fontsize = 18)
    barplt.set_title("How many entries there are for each category",
                     fontsize = 20)

    barplt.set_xticklabels(barplt.get_xticklabels(), rotation = 90,
                           fontsize = 16)
    fig = barplt.get_figure()
    fig.savefig(viz_path + "categories_barplot.png")
    plt.close()


def tags_by_category_barplot(search_tags, filename, title, stacked):
    manuscript_version = "tl" # "tl", "tc" or "tcn"

    tags = []
    categories = []

    all_entries = []
    all_entry_categories = []

    entry = None

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = f'{manuscript_version}_p{number}{side}_preTEI'
        input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

        tree = etree.parse(input_filename)

        for div in tree.findall(".//div"):
            new_entry = div.get("id")
            if new_entry != None:
                entry = new_entry
            if entry == None:
                continue

            entry_text = etree.tostring(div, method = "xml", encoding="UTF-8").decode('utf-8')

            category_list = div.get("categories")
            if isinstance(category_list, str):
                category_list = category_list.split(";")
            if category_list == None:
                # find the categories if this entry was already seen
                category_list = []
                for j in range(len(all_entries)):
                    if all_entries[j] == entry:
                        category_list.append(all_entry_categories[j])
            else:
                if entry not in all_entries:
                    for cat in category_list:
                        all_entries.append(entry)
                        all_entry_categories.append(cat)

            for tag in search_tags:
                count = entry_text.count(tag)
                for j in range(int(count)):
                    for cat in category_list:
                        tags.append(clean_tag(tag))
                        categories.append(cat)

    df = pandas.DataFrame({"tags": tags, "categories": categories})

    plt.subplots(figsize = (10, 10))
    plt.gcf().subplots_adjust(bottom = 0.35)
    if stacked:
        barplt = sns.countplot(x = "categories", data = df,
                               order = all_categories, palette = "deep")
        total_sum = len(tags)
        for p in barplt.patches:
            nb = format(p.get_height()/total_sum*100, '.2f')
            barplt.annotate(nb + "%", (p.get_x() + p.get_width()/2, p.get_height()),
                            ha = 'center', va = 'center', xytext = (0, 25),
                            textcoords = 'offset points', rotation = 90,
                            fontsize = 12)

        tl = ((barplt.get_xlim()[1] - barplt.get_xlim()[0])*0.8 + barplt.get_xlim()[0],
              (barplt.get_ylim()[1] - barplt.get_ylim()[0])*0.95 + barplt.get_ylim()[0])
        barplt.text(tl[0], tl[1], "Total count: " + str(total_sum))
    else:
        barplt = sns.countplot(x = "categories", hue = "tags", data = df,
                               order = all_categories)
        barplt.legend(fancybox = True)

    barplt.set_ylabel("Count", fontsize = 18)
    barplt.set_xlabel("Categories", fontsize = 18)
    barplt.set_title(title, fontsize = 20)

    barplt.set_xticklabels(barplt.get_xticklabels(), rotation = 90, fontsize = 16)
    fig = barplt.get_figure()
    fig.savefig(f"{viz_path}{filename}.png")
    plt.close()


def tagged_length_barplot(tags, xlabels, filename):
    ntags = len(tags)
    for manuscript_version in ["tc", "tcn", "tl"]:
        lengths = np.zeros(ntags)
        counts = np.zeros(ntags)

        for i in range(340):
            number = format(i//2 + 1, '03')
            side = "r" if (i % 2 == 0) else "v"

            folio = f'{manuscript_version}_p{number}{side}_preTEI'
            input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

            tree = etree.parse(input_filename)

            for j in range(ntags):
                tag = clean_tag(tags[j])
                for e in tree.findall(".//" + tag):
                    tag_text = etree.tostring(e, method = "text", encoding="UTF-8").decode('utf-8')
                    lengths[j] += len(tag_text.split())
                    counts[j] += 1

        data = [lengths[i]/counts[i] for i in range(ntags)]

        plt.subplots(figsize = (10, 10))
        plt.gcf().subplots_adjust(bottom = 0.25)
        barplt = sns.barplot(x = tags, y = data, palette = "deep")

        barplt.set_ylabel("Average number of words inside tag", fontsize = 16)
        barplt.set_xlabel("Tag", fontsize = 16)
        barplt.set_title(f"How many words there inside a tag [{manuscript_version}]",
                         fontsize = 18)
        barplt.set_xticklabels(xlabels, rotation = 90, fontsize = 14)

        fig = barplt.get_figure()
        fig.savefig(f"{viz_path}{manuscript_version}_{filename}.png")
        plt.close()


def entries_lengths_scatterplot(logscale):
    for manuscript_version in ["tc", "tcn", "tl"]:

        entries = []
        lengths = []
        normalized_lengths = []
        folios = []

        entry = None

        for i in range(0, 340):
            number = format(i//2 + 1, '03')
            side = "r" if (i % 2 == 0) else "v"

            folio = f'{manuscript_version}_p{number}{side}_preTEI'
            input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

            tree = etree.parse(input_filename)

            for div in tree.findall(".//div"):
                new_entry = div.get("id")
                if new_entry != None:
                    entry = new_entry
                if entry == None:
                    continue

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

        df = pandas.DataFrame({"entries": entries, "lengths": lengths,
                               "normalized_lengths": normalized_lengths,
                               "folio number": folios})

        max_words = np.max(lengths)
        max_diff_words = np.max(normalized_lengths)
        minmax = np.min([max_words, max_diff_words])

        ratios = [lengths[i]/normalized_lengths[i] for i in range(len(lengths))]
        mean_ratio = np.mean(ratios)

        plt.subplots(figsize = (10, 10))
        #plt.gcf().subplots_adjust(left = 0.05)
        #plt.gcf().subplots_adjust(right = 0.95)
        #points = plt.scatter(df["lengths"], df["normalized_lengths"], s = 0)
        #plt.colorbar(points)

        scatter = sns.scatterplot(x = "lengths", y = "normalized_lengths",
                                  hue = "folio number", data = df,
                                  linewidth = 0.4, alpha = 1, size_norm = 1,
                                  palette = "plasma", edgecolor = "k")

        for line in range(0, df.shape[0]):
            if (df.lengths[line] > 1500):
                scatter.text(df.lengths[line] + 30, df.normalized_lengths[line],
                             df.entries[line], horizontalalignment = "left",
                             fontsize = 10)
            if (df.lengths[line] < 2 and logscale):
                scatter.text(df.lengths[line]*1.1, df.normalized_lengths[line],
                             df.entries[line], horizontalalignment = "left",
                             fontsize = 10)
            if (df.entries[line] == "p162r_1" or df.entries[line] == "p001r_3"):
                scatter.text(df.lengths[line] - 10, df.normalized_lengths[line],
                             df.entries[line], horizontalalignment = "right",
                             fontsize = 10)

        scatter.set_xlabel("Number of words", fontsize = 16)
        scatter.set_ylabel("Number of different words", fontsize = 16)
        if logscale:
            scatter.set(xscale = "log")
            scatter.set(yscale = "log")
            scatter.set_title(f"Lengths of entries (logscale) [{manuscript_version}]",
                              fontsize = 20)
        else:
            scatter.set_title(f"Lengths of entries [{manuscript_version}]",
                              fontsize = 20)

        scatter.legend(fancybox = True)

        scatter.plot([1, minmax], [1, minmax], "--g")
        scatter.text(minmax, minmax + 10, "1:1 ratio",
                     horizontalalignment = "center", fontsize = 10, color = "g")

        ratios = [lengths[i]/normalized_lengths[i] for i in range(len(lengths))]
        mean_ratio = np.mean(ratios)
        scatter.plot([1, minmax*mean_ratio], [1, minmax], "--b", alpha = 1)
        if logscale:
            scatter.text(minmax*mean_ratio, minmax + 200, "mean ratio",
                         horizontalalignment = "center", fontsize = 10,
                         color = "b")
        else:
            scatter.text(minmax*mean_ratio, minmax + 10, "mean ratio",
                         horizontalalignment = "center", fontsize = 10,
                         color = "b")

        fig = scatter.get_figure()
        if logscale:
            fig.savefig(f"{viz_path}{manuscript_version}_entries_lengths_scatterplot_logscale.png")
        else:
            fig.savefig(f"{viz_path}{manuscript_version}_entries_lengths_scatterplot_linearscale.png")
        plt.close()


def entries_lengths_distplot():
    for manuscript_version in ["tc", "tcn", "tl"]:

        lengths = []
        normalized_lengths = []

        entry = None

        for i in range(0, 340):
            number = format(i//2 + 1, '03')
            side = "r" if (i % 2 == 0) else "v"

            folio = f'{manuscript_version}_p{number}{side}_preTEI'
            input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

            tree = etree.parse(input_filename)

            for div in tree.findall(".//div"):
                new_entry = div.get("id")
                if new_entry != None:
                    entry = new_entry
                if entry == None:
                    continue

                entry_text = etree.tostring(div, method = "text", encoding="UTF-8").decode('utf-8')
                entry_words = entry_text.split()
                number_of_words = len(entry_words)
                number_of_different_words = len(list(dict.fromkeys(entry_words))) # duplicates removed
                lengths.append(number_of_words)
                normalized_lengths.append(number_of_different_words)

        df = pandas.DataFrame({"lengths": lengths, "normalized_lengths": normalized_lengths})

        plt.subplots(figsize = (10, 10))
        #plt.gcf().subplots_adjust(left = 0.05)
        #plt.gcf().subplots_adjust(right = 0.95)

        distplt = sns.distplot(a = df["normalized_lengths"], kde = True, color = "r",
                               kde_kws = {"color": "r", "lw": 3, "label": "Number of differents words per entry", "alpha": 0.7},
                               bins = np.linspace(0, 800, 40))
        distplt = sns.distplot(a = df["lengths"], kde = True, color = "b",
                               kde_kws = {"color": "b", "lw": 3, "label": "Total number of words per entry", "alpha": 0.7},
                               bins = np.linspace(0, 800, 40))

        distplt.set_xlabel("Word counts")
        distplt.set_title(f"Density estimate of the lengths of entries [{manuscript_version}]",
                          fontsize = 20)
        distplt.set_yticklabels([])
        distplt.set_xlim(0, 900)
        distplt.legend(fancybox = True)

        fig = distplt.get_figure()
        fig.savefig(f"{viz_path}{manuscript_version}_entries_lengths_distplot.png")
        plt.close()


def tags_by_category_swarmplot(search_tags, filename, title):
    manuscript_version = "tl" # "tl", "tc" or "tcn"

    # for the swarmplot
    entries = []
    entry_ids = []
    tags = []
    categories = []
    entry_count = 0

    # for the stripplot
    entries2 = []
    entry_ids2 = []
    categories2 = []

    all_entries = [] # used for getting entry ids (necessary for the x axis)
    xlabels = [""] # will be the labels on the x axis

    entry = None

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = f'{manuscript_version}_p{number}{side}_preTEI'
        input_filename = f'{m_path}/ms-xml/{manuscript_version}/{folio}.xml'

        tree = etree.parse(input_filename)

        for div in tree.findall(".//div"):
            new_entry = div.get("id")
            if new_entry != None:
                entry = new_entry
            if entry == None:
                continue

            if entry not in all_entries:
                id = len(all_entries)
                all_entries.append(entry)
                if id % 25 == 0:
                    xlabels.append(entry)
            else:
                for j in range(len(all_entries)):
                    if all_entries[j] == entry:
                        id = j
                        break

            entry_text = etree.tostring(div, method = "xml", encoding="UTF-8").decode('utf-8')
            category_list = div.get("categories")
            if isinstance(category_list, str):
                category_list = category_list.split(";")
            if category_list == None:
                # find the categories if this entry was already seen
                category_list = []
                for j in range(len(entries2)):
                    if entries2[j] == entry:
                        category_list.append(categories2[j])

            for tag in search_tags:
                count = entry_text.count(tag)
                for j in range(int(count)):
                    for cat in category_list:
                        entries.append(entry)
                        entry_ids.append(id)
                        tags.append(clean_tag(tag))
                        categories.append(cat)

            for cat in category_list:
                entries2.append(entry)
                entry_ids2.append(id)
                categories2.append(cat)

    df_swarm = pandas.DataFrame({"tags": tags, "entry_ids": entry_ids,
                                 "categories": categories})
    df_strip = pandas.DataFrame({"entry_ids": entry_ids2,
                                 "categories": categories2})

    plt.subplots(figsize = (21, 15))
    plt.gcf().subplots_adjust(right = 0.99)

    swarm = sns.stripplot(x = "entry_ids", y = "categories", data = df_strip,
                          color = "0.7", jitter = 0, size = 12, marker = "$|$",
                          order = all_categories)
    swarm = sns.swarmplot(x = "entry_ids", y = "categories", hue = "tags",
                          dodge = True, data = df_swarm, size = 4,
                          order = all_categories)

    swarm.xaxis.set_major_locator(ticker.MultipleLocator(25))
    swarm.xaxis.set_major_formatter(ticker.ScalarFormatter())

    swarm.grid(False)
    swarm.set_ylabel("Categories", fontsize = 20)
    swarm.set_xlabel("Entries", fontsize = 20)
    swarm.set_title(title, fontsize = 24)

    swarm.set_xticklabels(xlabels, rotation = 90, fontsize = 12)
    swarm.set_yticklabels(swarm.get_yticklabels(), fontsize = 12)
    swarm.legend(fancybox = True)

    fig = swarm.get_figure()
    fig.savefig(f"{viz_path}{filename}.png")
    plt.close()


viz_dir = f'{m_path}/manuscript-object/manuscript_visualizations/'

if not os.path.exists(viz_dir):
    os.mkdir(viz_dir)

language_tags = ["<fr>", "<el>", "<it>", "<la>", "<oc>", "<po>"]
languages = ["French", "Greek", "Italian", "Latin", "Occitan", "Poitevin"]
margin_types = ["left-bottom", "right-bottom", "bottom", "right-middle",
                "left-middle", "right-top", "left-top", "top"]
semantic_tags = ["<al>", "<bp>", "<cn>", "<env>", "<m>", "<md>", "<ms>", "<mu>",
                 "<pa>", "<pl>", "<pn>", "<pro>", "<sn>", "<tl>", "<tmp>",
                 "<wp>"]
semantic_tags_legend = ["animal (al)", "body part (bp)", "currency (cn)",
                        "environment (env)", "material (m)", "medical (md)",
                        "measurement (ms)", "music (mu)", "plant (pa)",
                        "place (pl)", "personal name (pn)", "profession (pro)",
                        "sensory (sn)", "tool (tl)", "temporal (tmp)",
                        "arms and armor (wp)"]
insertion_marks = ["<mark>X", "<mark>+", "<mark>#"]
insertion_marks_legend = ["X", "+", "#"]
other_tags = ["df"]
other_tags_legend = ["definition"]

#tags_scatterplot(language_tags, "languages_scatterplot", title)

viz_path = viz_dir + "bubbleplots/"

if not os.path.exists(viz_path):
    os.mkdir(viz_path)

tags_bubbleplot(language_tags, languages, "languages_bubbles", "Other languages in the English translation of the manuscript")
tags_bubbleplot(["<del>", "<add>"], ["additions", "deletions"], "add_del_bubbles", "Additions and deletions by the author-practitioner")
tags_bubbleplot(margin_types, margin_types, "margins_bubbles", "Margins in the manuscript")
tags_bubbleplot(semantic_tags, semantic_tags_legend, "semantic_tags_bubbles", "Semantic tags in the manuscript")

print("Bubbleplots finished.")

viz_path = viz_dir + "barplots/"

if not os.path.exists(viz_path):
    os.mkdir(viz_path)

categories_barplot()

tags_by_category_barplot(["<del>", "<add>"], "add_del_tag_by_category_barplot", "Additions and deletions by the author-practitioner", False)
tags_by_category_barplot(["<add>"], "add_tag_by_category_barplot", "Additions by the author-practitioner", True)
tags_by_category_barplot(["<del>"], "del_tag_by_category_barplot", "Deletions by the author-practitioner", True)
tags_by_category_barplot(margin_types, "margins_by_category_barplot", "Margins in the manuscript", True)
tags_by_category_barplot(["</figure>", "</mark>"], "figures_marks_barplot", "Figures and marks in the manuscript", False)
tags_by_category_barplot(insertion_marks, "insertion_marks_barplot", "Insertion marks in the manuscript", True)

for i in range(len(language_tags)):
    tag = language_tags[i]
    language = languages[i]
    tags_by_category_barplot([tag], clean_tag(tag) + "_tag_by_category_barplot",
                             language + " in the manuscript", True)

for i in range(len(semantic_tags)):
    tag = semantic_tags[i]
    legend = semantic_tags_legend[i]
    tags_by_category_barplot([tag], clean_tag(tag) + "_tag_by_category_barplot",
                             legend + " tags", True)

for i in range(len(other_tags)):
    tag = other_tags[i]
    legend = other_tags_legend[i]
    tags_by_category_barplot([tag], clean_tag(tag) + "_tag_by_category_barplot",
                             legend + " tags", True)

tagged_length_barplot(semantic_tags, semantic_tags_legend, "semantic_tags_size_barplot")

print("Barplots finished.")

viz_path = viz_dir + "scatterplots/"

if not os.path.exists(viz_path):
    os.mkdir(viz_path)

entries_lengths_scatterplot(True)
entries_lengths_scatterplot(False)

print("Scatterplots finished.")

viz_path = viz_dir + "distplots/"

if not os.path.exists(viz_path):
    os.mkdir(viz_path)

entries_lengths_distplot()

print("Distplots finished.")

viz_path = viz_dir + "swarmplots/"

if not os.path.exists(viz_path):
    os.mkdir(viz_path)

tags_by_category_swarmplot(["<del>", "<add>"], "add_del_swarmplot", "Additions and deletions by the author-practitioner")
tags_by_category_swarmplot(margin_types, "margins_swarmplot", "Margins in the manuscript")
tags_by_category_swarmplot(language_tags, "languages_swarmplot", "Other languages in the English translation of the manuscript")
tags_by_category_swarmplot(["</figure>", "</mark>"], "figures_marks_swarmplot", "Figures and marks in the manuscript")
tags_by_category_swarmplot(insertion_marks, "insertion_marks_swarmplot", "Insertion marks in the manuscript")

for i in range(len(semantic_tags)):
    tag = semantic_tags[i]
    legend = semantic_tags_legend[i]
    tags_by_category_swarmplot([tag], clean_tag(tag) + "_tag_swarmplot",
                               legend + " tags in the manuscript")

for i in range(len(other_tags)):
    tag = other_tags[i]
    legend = other_tags_legend[i]
    tags_by_category_swarmplot([tag], clean_tag(tag) + "_tag_swarmplot",
                               legend + " tags in the manuscript")

print("Swarmplot finished.")

print("All done!")
