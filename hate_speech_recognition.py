# -*- coding: utf-8 -*-
"""Hate_Speech_Recognition.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tlchFjqlbHUtlkNBxBN0YT7i3vFwby2_
"""

from google.colab import drive
drive.mount('/content/gdrive')

"""
# This Python 3 environment comes with many helpful analytics libraries installed
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

import os
for dirname, _, filenames in os.walk('path goes here..'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
"""

pip install stop_words

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import re
import nltk
#from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from mlxtend.plotting import plot_confusion_matrix
from sklearn import preprocessing
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, MaxPool1D, Dropout, Dense, GlobalMaxPooling1D, Embedding, Activation
from keras.utils import to_categorical
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from stop_words import get_stop_words

"""# **Importing dataset , dropping unnamed columns and ceeating a test data**

---


"""

train_data_path = '/content/gdrive/My Drive/Colab Notebooks/Hate Speech Recognition/data/'
train_data = pd.read_csv(train_data_path + 'train.csv')

train_data = train_data.loc[:, ~train_data.columns.str.contains('^Unnamed')]

print('original train data shape',train_data.shape)

#test_data = train_data.iloc[137571:,:]
#test_data = test_data.reset_index()
#train_data = train_data.iloc[:137570,:]

#print('test data shape',test_data.shape)
#print('new train data shape',train_data.shape)
#print(test_data.shape[0]+train_data.shape[0])

train_data.head(5)

"""
# **Preprocessing the dataset**


---

"""

def deleteSmallWords(text):
    return ' '.join([word for word in text.split() if len(word) > 3])   
def cleanText(text):
    # clean the text
    text = re.sub(r"Https?://[A-Za-z0-9./]+","url",text)
    text = re.sub(r"[^A-Za-z0-9^,!.\/'+-=]"," ",text)
    text = re.sub(r"what's","what is ",text)
    text = re.sub(r"\'s"," ",text)
    text = re.sub(r"\s+[a-zA-Z]\s+", ' ', text) # Single character removal
    text = re.sub(r"\'ve"," have ",text)
    text = re.sub(r"\n't"," not ",text)
    #text = re.sub(r"\i'm","i am ",text)
    text = re.sub(r"\'re"," are ",text)
    text = re.sub(r"\'d"," would ",text)
    text = re.sub(r"\'ll"," will ",text)
    text = re.sub(r"\."," ",text)
    text = re.sub(r"!"," ",text)
    text = re.sub(r"\/"," ",text)
    text = re.sub(r"\^"," ^ ",text)
    text = re.sub(r"\+"," + ",text)
    text = re.sub(r"\-"," - ",text)
    text = re.sub(r"\="," = ",text)
    text = re.sub(r":"," : ",text)
    text = re.sub(r"'"," ",text)
    text = re.sub(r"(\d+)(k)",r"\g<1>000",text)
    text = re.sub(r" e g "," eg ",text)
    text = re.sub(r" b g "," bg ",text)
    text = re.sub(r" u s "," amarican ",text)
    text = re.sub(r"\0s","0",text)
    text = re.sub(r" 9 11 ","911",text)
    text = re.sub(r"e - mail","email",text)
    text = re.sub(r"j k","jk",text)
    text = re.sub(r"\s{2,}"," ",text)
    text = re.sub(r"@[A-Za_z0-9]+",'',text)
    text = re.sub(r"(\w)\1{2,}",r"\1\1",text)
    text = re.sub(r"\w(\w)\1{2}",'',text)
    return text
def deleteNonAlphaWords(text):
    return ''.join([word for word in text.split() if word.isalpha()])
def deleteStopWords(text):
    return ' '.join([word for word in text.lower().split() if not word in get_stop_words('english') and len(word) >= 3])

train_data['comment_text'] = train_data['comment_text'].apply(lambda text:deleteSmallWords(text))
train_data['comment_text'] = train_data['comment_text'].apply(lambda text:cleanText(text))
train_data['comment_text'] = train_data['comment_text'].apply(lambda text:deleteNonAlphaWords(text))
train_data['comment_text'] = train_data['comment_text'].apply(lambda text:deleteStopWords(text))

#test_data['comment_text'] = test_data['comment_text'].apply(lambda text:deleteSmallWords(text))
#test_data['comment_text'] = test_data['comment_text'].apply(lambda text:cleanText(text))
#test_data['comment_text'] = test_data['comment_text'].apply(lambda text:deleteNonAlphaWords(text))
#test_data['comment_text'] = test_data['comment_text'].apply(lambda text:deleteStopWords(text))

"""# **Tokenize the data**

---


"""

num_texts = len(train_data.index)
print(num_texts)
token = Tokenizer(num_words=num_texts)
token.fit_on_texts(train_data['comment_text'])
text = token.texts_to_sequences(train_data['comment_text'])
text = pad_sequences(text)

tt = 'bitch hate nigga'
text_test = token.texts_to_sequences(tt)
text_test = pad_sequences(text_test)
print(type(text_test))

columns = train_data.columns
columns = list(columns[2:])
print(columns)
#y = train_data.loc[:,columns].values
y = train_data['toxic']
print(text.shape,y.shape)
print(text[1],y[0])

x_train, x_test, y_train, y_test = train_test_split(text, y, test_size=0.2, random_state=1)
print(x_train.shape,x_test.shape)
print(y_train.shape,y_test.shape)
print(type(text))

max_features = num_texts
embedding_dim = 32

model = Sequential()
model.add(Embedding(max_features, embedding_dim))
model.add(Dropout(0.2))
model.add(LSTM(32, return_sequences=True))
model.add(Dropout(0.2))
model.add(Dense(1))
model.add(Activation('sigmoid'))
model.summary()

# compile and train model
print(x_train.shape,y_train.shape)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
history = model.fit(x_train, y_train, validation_data=(x_test, y_test), epochs=10)

#model.predict(text_test)