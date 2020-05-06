import csv
import os

from lxml import etree

#from digital_manuscript import BnF

#manuscript = BnF()

cwd = os.getcwd()
#m_path = cwd if 'manuscript-object' not in cwd else f'{cwd}/../m-k-manuscript-data'
#m_k_data_to_context = f'{m_path}/manuscript-object/context'
#
#if not os.path.exists(m_k_data_to_context):
#  os.mkdir(m_k_data_to_context)

#os.mkdir("context")

ms_xml_path = cwd + "/../ms-xml/"

tag = "al" # which tag we're looking for
property = "animal"
manuscript_version = "tl" # "tl", "tc" or "tcn"

output_filename = "context/context_" + manuscript_version + "_" + tag + "_tags.csv"
out_file = open(output_filename, 'w')
writer = csv.writer(out_file)
writer.writerow(["folio", "text in tag", "before", "after"])

remove_chars = ["\n", "\t", "+", " -", "- ", "\"", ",", ".", "\'", "’"]
context_size = 10 # how many words taken on each side

for i in range(0, 340):
    number = format(i//2 + 1, '03')
    side = "r" if (i % 2 == 0) else "v"

    folio = manuscript_version + "_p" + number + side +"_preTEI"
    input_filename = ms_xml_path + manuscript_version + "/" + folio + ".xml"

    tree = etree.parse(input_filename)
    #root = tree.getroot()

    for block in tree.findall(".//ab"):
        already_found_in_block = [] # used in case we get the same word multiple times inside a block

        for item in block.findall(".//" + tag):
            # get text in tag and normalize
            tag_text = item.text

            if tag_text is None:
                continue

            for i in range(len(remove_chars)):
                tag_text = tag_text.replace(remove_chars[i], "" if i > 0 else " ")

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

            tag_text_limits = [text_list[0]]
            if len(text_list) > 1:
                tag_text_limits.append(text_list[-1])

            for word in word_list:
                for text in tag_text_limits:
                    if (text in word) and (word != text):
                        # case where tag_text got stuck with other words when removing XML tags
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
            idx1 = -1
            for i in range(len(word_list)):
                if (word_list[i] == tag_text):
                    if (countdown == 0):
                        # that's the good one
                        idx1 = i
                        break
                    else:
                        countdown-=1
            idx2 = idx1 + 1

            if (idx1 == -1):
                # there are spaces inside tag_text
                # so we have to find it another way

                countdown = already_found_in_block.count(tag_text)

                for i in range(len(word_list) - len(text_list)): # fix???
                    correct_match = True
                    for j in range(len(text_list)):
                        if text_list[j] != word_list[i + j]:
                            correct_match = False
                            break
                    if correct_match:
                        # we found text_list inside of word_list
                        if (countdown == 0):
                            # that's the good one
                            idx1 = i
                            idx2 = i + len(text_list)
                            break
                        else:
                            # we already found that one before
                            countdown -= 1

            # if len(indices) == 0:
            #     # no exact occurence
            #     for word in word_list:
            #         if tag_text in word:
            #             idx = word_list.index(word)
            #             break

            before = word_list[max(0, idx1 - context_size):idx1]
            after = word_list[idx2:min(idx2 + context_size, len(word_list))]

            writer.writerow([folio, item.text.replace("\n", ""), before, after])
            already_found_in_block.append(tag_text)
