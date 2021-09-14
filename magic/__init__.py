#!/usr/bin/env python3

import glob
import os
import pickle

from lxml import html
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from model.schema.feeds import Language

dir_path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
    "clf.d",
)

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

def train_classifier(user_id, lang, likes, dislikes):
    if not likes:
        raise ValueError("No likes.")

    if not dislikes:
        raise ValueError("No dislikes.")

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

def compute_score(user_id, lang, items):
    clf_path = os.path.join(
        dir_path,
        str(user_id),
        lang.name + ".pickle",
    )
    with open(clf_path, 'rb') as f:
        clf = pickle.load(f)

    titles = [build_feature(row_it) for row_it in items]
    targets = clf.predict_proba(titles)
    scores = 2. * targets[:, 1] - 1.

    return scores

def trained_languages(user_id):
    user_path = os.path.join(dir_path, str(user_id))
    clf_path = os.path.join(user_path, "*.pickle")
    clf_paths = glob.glob(clf_path)

    extract_lang = lambda x: re.search(
        rf"(?<=^{user_path})\w+(?=\.pickle$)",
        x,
    ).group()

    return [Language[extract_lang(e)] for e in clf_paths]
