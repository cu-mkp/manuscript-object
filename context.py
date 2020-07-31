""" Data transform to generate a folder of .csv files containing the context for the text inside tags. """
# Python Modules
import csv
import os

# Third-Party Modules
from lxml import etree


def analyse_block(block, folio, writer):
    already_found_in_block = [] # used in case we get the same word multiple times inside a block

    for item in block.findall(".//" + tag):
        # get text in tag and normalize
        tag_text = item.text

        if (tag_text is None):
            continue

        try:
            for i in range(len(remove_chars)):
                tag_text = tag_text.replace(remove_chars[i], "" if i > 2 else " ")
                # '\n', '\'' and "’" are replaced by ""
                # all others by " "

            # get first parent block node
            p = item.getparent()
            while (p.tag != "ab"):
                p = p.getparent()

            # get all surrounding text (from parent block text) and normalize
            block_text = etree.tostring(p, method = "text", encoding="UTF-8").decode('utf-8')
            for c in remove_chars:
                block_text = block_text.replace(c, " ")
            word_list = block_text.split()

            text_list = tag_text.split()

            if len(text_list) == 0:
                continue

            tag_text_limits = [text_list[0]]
            if len(text_list) > 1:
                tag_text_limits.append(text_list[-1])

            for word in word_list:
                for text in tag_text_limits:
                    other_words_in_tag_text = text_list.copy()
                    other_words_in_tag_text.remove(text)
                    if (text in word) and (word != text) and (word not in other_words_in_tag_text) and (text not in dont_cut):
                        # case where text got stuck with other words when removing XML tags
                        i = word.find(text)
                        insert_list = [text]

                        # word = BLABLA1tag_textBLABLA2
                        subword1 = word[:i] # BLABLA1
                        if (len(subword1) != 0):
                            insert_list.insert(0, subword1)
                        subword2 = word[len(text) + i:] # BLABLA2
                        if (len(subword2) != 0):
                            insert_list.append(subword2)

                        i = word_list.index(word)
                        word_list[i:i+1] = insert_list

            # find the index of tag_text in word_list
            # considering it might appear multiple times
            countdown = already_found_in_block.count(tag_text)
            for i in range(len(word_list) - len(text_list) + 1):
                correct_match = True
                for j in range(len(text_list)):
                    if text_list[j] != word_list[i + j]:
                        correct_match = False
                        break
                if correct_match:
                    # we found text_list inside of word_list
                    if (countdown == 0):
                        # it's the good one
                        idx1 = i
                        idx2 = i + len(text_list)
                        break
                    else:
                        # we already found that one before
                        countdown -= 1

            before = word_list[max(0, idx1 - context_size):idx1]
            after = word_list[idx2:min(idx2 + context_size, len(word_list))]

            writer.writerow([folio, item.text.replace("\n", ""), before, after])
            already_found_in_block.append(tag_text)
        except (ValueError, UnboundLocalError):
            print("Error for \"" + tag_text + "\" in " + folio)

def analyse_folio(folio, writer):
    input_filename = m_path + "/ms-xml/" + manuscript_version + "/" + folio + ".xml"

    tree = etree.parse(input_filename)
    #root = tree.getroot()

    for block in tree.findall(".//ab"):
        analyse_block(block, folio, writer)

def get_context(tag):
    output_path = m_k_data_to_context + "/"
    output_filename = output_path + "context_" + manuscript_version + "_" + tag + "_tags.csv"
    out_file = open(output_filename, 'w')
    writer = csv.writer(out_file)
    writer.writerow(["folio", "text in tag", "before", "after"])

    for i in range(0, 340):
        number = format(i//2 + 1, '03')
        side = "r" if (i % 2 == 0) else "v"

        folio = manuscript_version + "_p" + number + side +"_preTEI"
        analyse_folio(folio, writer)


manuscript_version = "tcn" # "tl", "tc" or "tcn"

cwd = os.getcwd()
#print(cwd)
m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../'
m_k_data_to_context = f'{m_path}/manuscript-object/context'

if not os.path.exists(m_k_data_to_context):
    os.mkdir(m_k_data_to_context)

tags = ["al", "bp", "cn", "env", "m", "md", "ms", "mu", "pa", "pl", "pn", "pro", "sn", "tl", "tmp", "wp"] # which tags we're looking for
remove_chars = ["\n", "\'", "’", "\t", "+", " -", "- ", "\"", ",", "."] # characters to remove from words

context_size = 10 # how many words taken on each side

for manuscript_version in ["tc", "tcn", "tl"]:
    m_k_data_to_context = f'{m_path}/manuscript-object/context/{manuscript_version}'

    if not os.path.exists(m_k_data_to_context):
        os.mkdir(m_k_data_to_context)

    if (manuscript_version == "tl"):
        dont_cut = ["a", "in", "on", "or", "at", "as", "the"] # words that shouldn't cut other words (e.g. "in" inside "rain")
    else:
        dont_cut = ["de", "le", "la", "du", "a", "verd", "gris", "huille"]

    for tag in tags:
        get_context(tag)
        print("[" + manuscript_version + "] tag " + tag + " complete")

print("All done!")
