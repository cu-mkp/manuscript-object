# Python Modules
import csv
import sys
import os

cwd = os.getcwd()
m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'
m_k_data_to_context = f'{m_path}/manuscript-object/context'

if not os.path.exists(m_k_data_to_context):
    sys.exit("Error: no context directory found")

tags = ["al", "bp", "cn", "env", "m", "md", "ms", "mu", "pa", "pl", "pn", "pro", "sn", "tl", "tmp", "wp"] # which tags we're looking for
manuscript_version = "tl" # "tl", "tc" or "tcn"

def filter_stropwords(word):
    stopwords = ["ourselves", "hers", "between", "yourself", "but", "again", "there", "about", "once", "during", "out", "very", "having", "with", "they", "own", "an", "be", "some", "for", "do", "its", "yours", "such", "into", "of", "most", "itself", "other", "off", "is", "s", "am", "or", "who", "as", "from", "him", "each", "the", "themselves", "until", "below", "are", "we", "these", "your", "his", "through", "don", "nor", "me", "were", "her", "more", "himself", "this", "down", "should", "our", "their", "while", "above", "both", "up", "to", "ours", "had", "she", "all", "no", "when", "at", "any", "before", "them", "same", "and", "been", "have", "in", "will", "on", "does", "yourselves", "then", "that", "because", "what", "over", "why", "so", "can", "did", "not", "now", "under", "he", "you", "herself", "has", "just", "where", "too", "only", "myself", "which", "those", "i", "after", "few", "whom", "t", "being", "if", "theirs", "my", "against", "a", "by", "doing", "it", "how", "further", "was", "here", "than"]
    if word in stopwords:
        return False
    else:
        return True

all_context = []

for tag in tags:
    filename = m_k_data_to_context + "/" + manuscript_version + "/context_" + manuscript_version + "_" + tag + "_tags.csv"
    this_context = []

    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count > 0:
                str = row[2] + row[3]
                remove_chars = ["[", "]", "'", ",", '&']
                for char in remove_chars:
                    str = str.replace(char, "")
                word_list = str.split()
                word_list = filter(filter_stropwords, word_list)
                if word_list != []:
                    this_context += word_list
            line_count += 1

    all_context.append(this_context)
