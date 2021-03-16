import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import csv
from PIL import Image

path_g = "thesaurus/"
paths=["animal.csv","body_part.csv", "currency.csv", "environment.csv","material.csv","measurement.csv","medical.csv","music.csv","personal_name.csv","place.csv","plant.csv","profession.csv","sensory.csv","time.csv","tool.csv","weapon.csv"]

for i in range(0,16):
    path = path_g + paths[i]
    with open(path, encoding="utf8") as file :
        reader = csv.reader(file)
        data=dict()
        count=0
        for row in reader :
            print(count)
            count+=1
            if row[0]!='freq':
                if row[2] in data :
                    data[row[2]]+=1
                else :
                    data[row[2]]=1
    print(data)

    wc = WordCloud(background_color="white",width=1000,height=1000, max_words=30,relative_scaling=0.5,normalize_plurals=False).generate_from_frequencies(data)
    plt.imshow(wc)
    plt.axis("off")
    plt.show()

