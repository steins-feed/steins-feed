#!/usr/bin/env python3

import html

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from steins_sql import get_cursor

def unescape(s):
    return html.unescape(html.unescape(s))

def build_feature(row):
    title = row['Title'] + " " + row['Summary']
    idx1 = title.find("<")
    while not idx1 == -1:
        idx2 = title.find(">", idx1)
        title = title[:idx1] + title[idx2+1:]
        idx1 = title.find("<")
    return unescape(title)

def handle_magic(qd):
    c = get_cursor()
    user = qd['user']

    clfs = dict()
    langs = [e[0] for e in c.execute("SELECT DISTINCT Feeds.Language FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}!=0".format(user)).fetchall()]

    for lang_it in langs:
        # Build pipeline.
        count_vect = ('vect', CountVectorizer())
        tfidf_transformer = ('tfidf', TfidfTransformer())
        if qd['classifier'] == 'Naive Bayes':
            clf = ('clf', MultinomialNB())
        elif qd['classifier'] == 'Logistic Regression':
            clf = ('clf', LogisticRegression())
        else:
            raise KeyError
        text_clf = Pipeline([count_vect, tfidf_transformer, clf])

        # Train classifiers.
        likes = c.execute("SELECT Items.* FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}=1 AND Language=?".format(user), (lang_it, )).fetchall()
        dislikes = c.execute("SELECT Items.* FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}=-1 AND Language=?".format(user), (lang_it, )).fetchall()

        titles = []
        titles += [build_feature(row_it) for row_it in likes]
        titles += [build_feature(row_it) for row_it in dislikes]

        targets = []
        targets += [1 for row_it in likes]
        targets += [-1 for row_it in dislikes]

        try:
            clf = text_clf.fit(titles, targets)
        except ValueError:
            continue
        clfs[lang_it] = clf

    return clfs

    # Test on training data.
    #predicted = text_clf.predict(titles)
    #print(predicted[:len(likes)])
    #print(predicted[len(likes):])
    #predicted_proba = text_clf.predict_proba(titles)
    #print([int(100 * (it[1] - it[0])) / 100. for it in predicted_proba[:len(likes)]])
    #print([int(100 * (it[1] - it[0])) / 100. for it in predicted_proba[len(likes):]])

if __name__ == "__main__":
    clfs = handle_magic({'user': "hansolo", 'classifier': 'Logistic Regression'})
    clf = clfs['English']
    count_vect = clf.named_steps['vect']
    tfidf_transformer = clf.named_steps['tfidf']
    lr_clf = clf.named_steps['clf']
    table = count_vect.vocabulary_.items()
    coeffs = lr_clf.coef_[0] * tfidf_transformer.idf_
    table = [row + (coeffs[row[1]], ) for row in table]
    table = sorted(table, key=lambda row: row[2])
    print("Least favorite:", [row[0] for row in table[:10]])
    print("Most favorite:", [row[0] for row in table[:-10:-1]])
