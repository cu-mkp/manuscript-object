""" Data visualizations of the context files. """
# Python Modules
import csv
import sys
import os

# Third-Party Modules
import numpy as np
import pandas
import seaborn as sns; sns.set()
import matplotlib.pyplot as plt

manuscript_version = "tl" # "tl", "tc" or "tcn"

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'
m_k_data_to_context = f'{m_path}/manuscript-object/context'
viz_path = f'{m_path}/manuscript-object/context_visualizations/{manuscript_version}'

if not os.path.exists(m_k_data_to_context):
    sys.exit("Error: no context directory found")

if not os.path.exists(viz_path):
    os.mkdir(viz_path)

viz_path = f'{viz_path}/{manuscript_version}_'

tags = ["al", "bp", "cn", "env", "m", "md", "ms", "mu", "pa", "pl", "pn", "pro",
        "sn", "tl", "tmp", "wp"] # which tags we're looking for
tag_names = ["animal (al)", "body part (bp)", "currency (cn)", "environment (en)",
             "material (m)", "medical (md)", "measurement (ms)", "music (mu)",
             "plant (pu)", "place (pl)", "personal name (pn)", "profession (pro)",
             "sensory (sn)", "tool (tl)", "temporal (tmp)", "arms and armor (wp)"]

def filter_stopwords(word):
    stopwords = ["ourselves", "hers", "between", "yourself", "but", "again",
                 "there", "about", "once", "during", "out", "very", "having",
                 "with", "they", "own", "an", "be", "some", "for", "do", "its",
                 "yours", "such", "into", "of", "most", "itself", "other",
                 "off", "is", "s", "am", "or", "who", "as", "from", "him",
                 "each", "the", "themselves", "until", "below", "are", "we",
                 "these", "your", "his", "through", "don", "nor", "me", "were",
                 "her", "more", "himself", "this", "down", "should", "our",
                 "their", "while", "above", "both", "up", "to", "ours", "had",
                 "she", "all", "no", "when", "at", "any", "before", "them",
                 "same", "and", "been", "have", "in", "will", "on", "does",
                 "yourselves", "then", "that", "because", "what", "over", "why",
                  "so", "can", "did", "not", "now", "under", "he", "you",
                  "herself", "has", "just", "where", "too", "only", "myself",
                  "which", "those", "i", "after", "few", "whom", "t", "being",
                  "if", "theirs", "my", "against", "a", "by", "doing", "it",
                  "how", "further", "was", "here", "than"]
    if word in stopwords:
        return False
    else:
        return True

def filter_digits(word):
    if word.isdigit():
        return False
    else:
        return True

all_items = []
all_context = []
all_items_without_duplicates = []
all_context_without_duplicates = []

for tag in tags:
    filename = m_k_data_to_context + "/" + manuscript_version + "/context_" + manuscript_version + "_" + tag + "_tags.csv"
    these_items = [] # interior of the tag
    this_context = [] # context of the tag

    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                tag_text = row[1].lower()
                context_text = (row[2] + row[3]).lower()
                remove_chars = ["[", "]", "'", ",", '&', "’"]
                for char in remove_chars:
                    tag_text = tag_text.replace(char, "")
                    context_text = context_text.replace(char, "")
                tag_word_list = tag_text.split()
                context_word_list = context_text.split()
                # remove stopwords
                tag_word_list = filter(filter_stopwords, tag_word_list)
                context_word_list = filter(filter_stopwords, context_word_list)
                # remove digits
                tag_word_list = filter(filter_digits, tag_word_list)
                context_word_list = filter(filter_digits, context_word_list)
                if tag_word_list != []:
                    these_items += tag_word_list
                if context_word_list != []:
                    this_context += context_word_list
            line_count += 1

    all_items.append(these_items)
    all_context.append(this_context)

    all_items_without_duplicates.append(list(dict.fromkeys(these_items)))
    all_context_without_duplicates.append(list(dict.fromkeys(this_context)))

# heatmap visualization
# how similar are contexts from different tags
def create_symmetrical_heatmap():
    matrix = []
    for i in all_context_without_duplicates:
        si = set(i)
        line = []
        for j in all_context_without_duplicates:
            sj = set(j)
            # how much of si and sj is in common
            line.append(len(si.intersection(sj))/len(si.union(sj))*100)
        matrix.append(line)

    df = pandas.DataFrame(matrix, index = tag_names, columns = tag_names)
    no_diag_mask = np.identity(len(tags))
    plt.subplots(figsize = (15, 15))
    plt.gcf().subplots_adjust(bottom = 0.2)
    plt.gcf().subplots_adjust(left = 0.2)
    heatmap = sns.heatmap(df, square = True, mask = no_diag_mask,
                          annot = True, annot_kws = {"size": 16},
                          cmap = sns.cm.rocket_r)
    heatmap.collections[0].colorbar.set_label("Percentage of similar words in 20-word surroundings",
                                              fontsize = 20)
    heatmap.set_title("How similar is the author-practioner's vocabulary\nwhen talking about two different topics [" + manuscript_version + "]",
                      fontsize = 22)
    heatmap.set_ylabel("Tags", fontsize = 20)
    heatmap.set_xlabel("Tags", fontsize = 20)
    heatmap.set_xticklabels(tag_names, size = 16)
    heatmap.set_yticklabels(tag_names, size = 16)
    fig = heatmap.get_figure()
    fig.savefig(viz_path + "symmetrical_heatmap.png")

# heatmap visualization
# how similar are contexts from different tags
def create_asymmetrical_heatmap():
    matrix = []
    for i in all_context_without_duplicates:
        si = set(i)
        line = []
        for j in all_context_without_duplicates:
            sj = set(j)
            # how much of si is in sj
            line.append(len(si.intersection(sj))/len(sj)*100)
        matrix.append(line)

    df = pandas.DataFrame(matrix, index = tag_names, columns = tag_names)
    no_diag_mask = np.identity(len(tags))
    plt.subplots(figsize = (15, 15))
    plt.gcf().subplots_adjust(bottom = 0.2)
    plt.gcf().subplots_adjust(left = 0.2)
    heatmap = sns.heatmap(df, square = True, mask = no_diag_mask,
                          annot = True, annot_kws = {"size": 16},
                          cmap = sns.cm.rocket_r)
    heatmap.collections[0].colorbar.set_label("Percentage of included words in 20-word surroundings",
                                              fontsize = 20)
    heatmap.set_title("How similar is the author-practioner's vocabulary\nwhen talking about two different topics [" + manuscript_version + "]",
                      fontsize = 22)
    heatmap.set_ylabel("How much of this tag's context vocabulary...", fontsize = 20)
    heatmap.set_xlabel("...is included in this tag's context vocabulary?", fontsize = 20)
    heatmap.set_xticklabels(tag_names, size = 16)
    heatmap.set_yticklabels(tag_names, size = 16)
    fig = heatmap.get_figure()
    fig.savefig(viz_path + "asymmetrical_heatmap.png")

# barplot visualization
# how diverse are contexts from different tags
def create_barplot(normalized):
    plt.subplots(figsize = (10,15))
    plt.gcf().subplots_adjust(bottom = 0.2)
    plt.gcf().subplots_adjust(left = 0.15)
    if normalized:
        data = [len(all_context_without_duplicates[i])/len(all_items[i]) for i in range(len(tags))]
        ylabel_appendix = ",\ndivided by the number of times this tag appears"
        filename_appendix = "_normalized"
    else:
        data = [len(all_context_without_duplicates[i]) for i in range(len(tags))]
        ylabel_appendix = ""
        filename_appendix = ""
    barplt = sns.barplot(x = tag_names, y = data,
                       palette = "deep")
    mean = np.mean(data)
    barplt.axhline(mean, ls='-', color = "grey")
    barplt.text(0, mean + 80, "Mean", fontsize = 16, color = "grey")
    for p in barplt.patches:
        if (normalized):
            nb = format(p.get_height(), '.2f')
        else:
            nb = int(p.get_height())
        barplt.annotate(nb, (p.get_x() + p.get_width() / 2., p.get_height()), ha = 'center', va = 'center', xytext = (0, 10), textcoords = 'offset points')
    barplt.set_ylabel("Number of unique words in 20-word surroundings" + ylabel_appendix,
                    fontsize = 20)
    barplt.set_xlabel("Tag", fontsize = 20)
    barplt.set_title("How diversified is the author-practioner's\nvocabulary when talking about... [" + manuscript_version + "]",
                   fontsize = 24)
    barplt.set_xticklabels(barplt.get_xticklabels(), rotation = 90, fontsize = 16)
    barplt.set_yticklabels(tag_names, size = 16)
    #hist.yaxis.set_major_locator(plt.FixedLocator(5))
    barplt.set(yscale = "log")
    fig = barplt.get_figure()
    fig.savefig(viz_path + "barplot" + filename_appendix + ".png")

create_symmetrical_heatmap()
create_asymmetrical_heatmap()
create_barplot(True)
create_barplot(False)
