#!/usr/bin/env python3

from lxml import html
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from model.utils.all import liked_items, disliked_items

def build_feature(row):
    tree = html.fromstring(row['Title'])
    return html.tostring(tree, encoding='unicode', method='text')

def kullback_leibler(q, p):
    ev_q = np.sum(list(q.values()))
    ev_p = np.sum(list(p.values()))

    res = 0.
    for k in set(p) & set(q):
        pq = q[k] / ev_q
        pp = p[k] / ev_p
        res += pp * np.log(pp / pq)

    return res

def train_classifier(user_id, lang):
    likes = liked_items(user_id, lang)
    dislikes = disliked_items(user_id, lang)
    if not likes or not dislikes:
        return None

    titles = []
    titles += [build_feature(row_it) for row_it in likes]
    titles += [build_feature(row_it) for row_it in dislikes]

    targets = []
    targets += [1 for row_it in likes]
    targets += [-1 for row_it in dislikes]

    # Build pipeline.
    count_vect = ('vect', CountVectorizer())
    #count_vect = ('vect', NLTK_CountVectorizer(lang_it))
    tfidf_transformer = ('tfidf', TfidfTransformer())
    nb_clf = ('clf', MultinomialNB(fit_prior=False))
    text_clf = Pipeline([count_vect, tfidf_transformer, nb_clf])

    # Train pipeline.
    text_clf.fit(titles, targets)
    return text_clf
