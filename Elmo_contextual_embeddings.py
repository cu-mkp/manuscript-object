# # ELMo
# 
# Note that you will need to use the non-GPU accelerated run-time on this notebook due to the large memory useage of the ELMo model.

# ## Imports:

import os
import numpy as np
import pandas as pd
import tensorflow.compat.v1 as tf
tf.disable_eager_execution()
import tensorflow_hub as hub
from sklearn import preprocessing

os.environ['TFHUB_CACHE_DIR'] = 'D:/danac/Documents/Info/M&K/m-k-manuscript-data/manuscript-object/tf_cache'


# If the below cell does not work on first try, restart the kernel and try again

#python -m spacy download en_core_web_md
import spacy
from spacy.lang.en import English
from spacy import displacy
nlp = spacy.load('en_core_web_md')


from IPython.display import HTML
import logging
#logging.getLogger('tensorflow').disabled = True #OPTIONAL - to disable outputs from Tensorflow


# ## Create sentence embeddings

url = "https://tfhub.dev/google/elmo/3"
path2=os.getcwd() + "/ELMo2"
path3=os.getcwd() + "/ELMo3"  #this is ELMo3
embed = hub.Module(path3)

import re

path = os.getcwd() + '/../allFolios/txt/all_tl.txt'
fileo = open(path,'r',encoding='utf-8')
text=fileo.read()
fileo.close()

text = text.lower().replace('\n', ' ').replace('\t', ' ').replace('\xa0',' ')
text = ' '.join(text.split())
doc = nlp(text)

counter=0
sentences = []
for i in doc.sents:
  if len(i)>1 and counter<200:
    sentences.append(i.string.strip())
    counter+=1
    
len(sentences)

sentences[100:110]

embeddings = embed(
    sentences,
    signature="default",
    as_dict=True)["default"]

gpu_options = tf.GPUOptions(allow_growth=True) 
with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:  
    sess.run(tf.global_variables_initializer())
    sess.run(tf.tables_initializer())
    x = sess.run(embeddings)


# ## Visualize the sentences using PCA and TSNE


from sklearn.decomposition import PCA

pca = PCA(n_components=50)
y = pca.fit_transform(x)

from sklearn.manifold import TSNE

y = TSNE(n_components=2).fit_transform(y)


import chart_studio.plotly as py
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

init_notebook_mode(connected=True)


data = [
    go.Scatter(
        x=[i[0] for i in y],
        y=[i[1] for i in y],
        mode='markers',
        text=[i for i in sentences],
    marker=dict(
        size=16,
        color = [len(i) for i in sentences], #set color equal to a variable
        opacity= 0.8,
        colorscale='Viridis',
        showscale=False
    )
    )
]
layout = go.Layout()
layout = dict(
              yaxis = dict(zeroline = False),
              xaxis = dict(zeroline = False)
             )
fig = go.Figure(data=data, layout=layout)
file = plot(fig, filename='Sentence_encode_elmo3_200.html')
