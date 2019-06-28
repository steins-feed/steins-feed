#!/usr/bin/env python3

import numpy as np
import os
import pickle

from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline

from steins_magic import build_feature
from steins_nltk import NLTK_CountVectorizer, LDA_CountVectorizer
from steins_sql import get_cursor

user = "hansolo"
clf = "Naive Bayes"
lang = "English"
no_topics = 10
no_words = 10
no_vocab = 100

dir_path = os.path.dirname(os.path.abspath(__file__))
user_path = dir_path + os.sep + user
clf_path = user_path + os.sep + clf

c = get_cursor()
likes = c.execute("SELECT Items.* FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}=1 AND Language=?".format(user), (lang, )).fetchall()
#dislikes = c.execute("SELECT Items.* FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}=-1 AND Language=?".format(user), (lang, )).fetchall()

titles = []
titles += [build_feature(row_it) for row_it in likes]
#titles += [build_feature(row_it) for row_it in dislikes]

# Build pipeline.
#count_vect = ('vect', NLTK_CountVectorizer(lang))
with open(clf_path + os.sep + "{}.pickle".format(lang), 'rb') as f:
    table = pickle.load(f)
vocabs = [e[0] for e in table[-no_vocab:]]
count_vect = ('vect', LDA_CountVectorizer(lang, vocabs))

tfidf_trans = ('tfidf', TfidfTransformer(norm=None))

lda_trans = ('clf', LatentDirichletAllocation(n_components=no_topics, max_iter=100, evaluate_every=1, verbose=1))
#lda_trans = ('clf', LatentDirichletAllocation(n_components=no_topics, learning_method='online', max_iter=100, evaluate_every=1, verbose=1))

#pipeline = Pipeline([count_vect, lda_trans])
pipeline = Pipeline([count_vect, tfidf_trans, lda_trans])

# Train classifier.
pipeline.fit(titles)

features = pipeline.named_steps['vect'].get_feature_names()
#features = pipeline.named_steps['vect'].vocabulary_nltk
#idf_factors = pipeline.named_steps['tfidf'].idf_
for topic_ct in range(no_topics):
    print("Topic #{}:".format(topic_ct))
    topic = pipeline.named_steps['clf'].components_[topic_ct, :]
    print(" ".join([features[i] for i in topic.argsort()[:-no_words-1:-1]]))
    #topic *= idf_factors
    #print(" ".join([features[i] for i in topic.argsort()[:-no_words-1:-1]]))

#features = pipeline.named_steps['vect'].get_feature_names()
##features = pipeline.named_steps['vect'].vocabulary_nltk
#word_atlas = pipeline.transform(features)
#for topic_ct in range(no_topics):
#    print("Topic #{}:".format(topic_ct))
#    topic = word_atlas[:, topic_ct]
#    print(" ".join([features[i] for i in topic.argsort()[:-no_words-1:-1]]))

#title_map = pipeline.transform(titles)
#title_categories = title_map.argmax(axis=1)
#for topic_ct in range(no_topics):
#    title_idx = np.where(title_categories == topic_ct)[0]
#    if title_idx.size < 5:
#        continue
#    print("Topic #{}:".format(topic_ct))
#    for i in title_idx:
#        print(titles[i])
#    break
