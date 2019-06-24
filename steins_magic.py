#!/usr/bin/env python3

import html
import lxml
from lxml.html import builder as E
import os

import numpy as np

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from steins_html import preamble, side_nav, top_nav
from steins_sql import get_cursor

dir_path = os.path.dirname(os.path.abspath(__file__))

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

def steins_learn(user, classifier):
    c = get_cursor()

    clfs = dict()
    langs = [e[0] for e in c.execute("SELECT DISTINCT Feeds.Language FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE {0}!=0".format(user)).fetchall()]

    for lang_it in langs:
        # Build pipeline.
        count_vect = ('vect', CountVectorizer())
        tfidf_transformer = ('tfidf', TfidfTransformer())
        if classifier == 'Naive Bayes':
            clf = ('clf', MultinomialNB())
        elif classifier == 'Logistic Regression':
            clf = ('clf', LogisticRegression())
        elif classifier == 'SVM':
            clf = ('clf', SVC(probability=True))
        elif classifier == 'Linear SVM':
            clf = ('clf', SVC(kernel='linear', probability=True))
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

def handle_analysis(user="nobody", clf="Naive Bayes"):
    c = get_cursor()
    scorers = steins_learn(user, clf)

    #--------------------------------------------------------------------------

    # Preamble.
    tree, head, body = preamble("Stein's Feed")

    #--------------------------------------------------------------------------

    # Scripts.
    for js_it in ["open_menu.js", "close_menu.js"]:
        script_it = E.SCRIPT()
        with open(dir_path + os.sep + "js" + os.sep + js_it, 'r') as f:
            script_it.text = f.read()
        head.append(script_it)

    #--------------------------------------------------------------------------

    # Top & side navigation menus.
    body.append(top_nav(user))
    body.append(side_nav(user=user, clf=clf))

    #--------------------------------------------------------------------------

    # Body.
    div_it = E.DIV(E.CLASS("main"))
    body.append(div_it)
    div_it.append(E.HR())

    langs = scorers.keys()

    #--------------------------------------------------------------------------

    tables = dict()
    for lang_it in langs:
        pipeline = scorers[lang_it]
        count_vect = pipeline.named_steps['vect']

        table = list(count_vect.vocabulary_.keys())
        coeffs = pipeline.predict_proba(table)
        coeffs = 2. * coeffs - 1.
        table = [(table[i], coeffs[i, 1], ) for i in range(len(table))]
        tables[lang_it] = sorted(table, key=lambda row: row[1])

    # Most favorite words.
    h_it = E.H2()
    h_it.text = "Most favorite words"
    div_it.append(h_it)

    table_it = E.TABLE()
    div_it.append(table_it)

    tr_it = E.TR()
    for lang_it in langs:
        td_it = E.TH()
        td_it.text = lang_it
        tr_it.append(td_it)
    table_it.append(tr_it)

    td_it = E.TD(colspan=str(len(langs)))
    td_it.append(E.HR())
    table_it.append(td_it)

    for i in reversed(range(-10, 0)):
        tr_it = E.TR()
        for lang_it in langs:
            td_it = E.TD()
            td_it.text = "{} ({:.2f})".format(tables[lang_it][i][0], tables[lang_it][i][1])
            tr_it.append(td_it)
        table_it.append(tr_it)

    # Least favorite words.
    h_it = E.H2()
    h_it.text = "Least favorite words"
    div_it.append(h_it)

    table_it = E.TABLE()
    div_it.append(table_it)

    tr_it = E.TR()
    for lang_it in langs:
        td_it = E.TH()
        td_it.text = lang_it
        tr_it.append(td_it)
    table_it.append(tr_it)

    td_it = E.TD(colspan=str(len(langs)))
    td_it.append(E.HR())
    table_it.append(td_it)

    for i in range(10):
        tr_it = E.TR()
        for lang_it in langs:
            td_it = E.TD()
            td_it.text = "{} ({:.2f})".format(tables[lang_it][i][0], tables[lang_it][i][1])
            tr_it.append(td_it)
        table_it.append(tr_it)

    div_it.append(E.HR())

    #--------------------------------------------------------------------------

    tables = dict()
    for lang_it in langs:
        pipeline = scorers[lang_it]
        count_vect = pipeline.named_steps['vect']

        feeds = [row[0] for row in c.execute("SELECT Title FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE Language=? AND Display.{}=1".format(user), (lang_it, )).fetchall()]
        coeffs = []
        for title_it in feeds:
            articles = [build_feature(row) for row in c.execute("SELECT * FROM Items WHERE Source=? ORDER BY Published DESC LIMIT 100", (title_it, )).fetchall()]
            if len(articles) == 0:
                coeffs.append(0.)
                continue
            articles_proba = pipeline.predict_proba(articles)
            articles_proba = np.log(articles_proba / (1. - articles_proba))
            coeff = np.sum(articles_proba[:, 1]) / (articles_proba.shape[0] + 10.)
            coeff = np.exp(coeff)
            coeff = 2. * coeff / (1. + coeff) - 1.
            coeffs.append(coeff)
        table = [(feeds[i], coeffs[i], ) for i in range(len(feeds))]
        tables[lang_it] = sorted(table, key=lambda row: row[1])

    # Most favorite feeds.
    h_it = E.H2()
    h_it.text = "Most favorite feeds"
    div_it.append(h_it)

    table_it = E.TABLE()
    div_it.append(table_it)

    tr_it = E.TR()
    for lang_it in langs:
        td_it = E.TH()
        td_it.text = lang_it
        tr_it.append(td_it)
    table_it.append(tr_it)

    td_it = E.TD(colspan=str(len(langs)))
    td_it.append(E.HR())
    table_it.append(td_it)

    for i in reversed(range(-5, 0)):
        tr_it = E.TR()
        for lang_it in langs:
            td_it = E.TD()
            td_it.text = "{} ({:.2f})".format(tables[lang_it][i][0], tables[lang_it][i][1])
            tr_it.append(td_it)
        table_it.append(tr_it)

    # Least favorite feeds.
    h_it = E.H2()
    h_it.text = "Least favorite feeds"
    div_it.append(h_it)

    table_it = E.TABLE()
    div_it.append(table_it)

    tr_it = E.TR()
    for lang_it in langs:
        td_it = E.TH()
        td_it.text = lang_it
        tr_it.append(td_it)
    table_it.append(tr_it)

    td_it = E.TD(colspan=str(len(langs)))
    td_it.append(E.HR())
    table_it.append(td_it)

    for i in range(5):
        tr_it = E.TR()
        for lang_it in langs:
            td_it = E.TD()
            td_it.text = "{} ({:.2f})".format(tables[lang_it][i][0], tables[lang_it][i][1])
            tr_it.append(td_it)
        table_it.append(tr_it)

    #--------------------------------------------------------------------------

    return lxml.html.tostring(tree, doctype="<!DOCTYPE html>", pretty_print=True).decode('utf-8')

def handle_highlight(qd):
    c = get_cursor()
    scorers = steins_learn(qd['user'], "Naive Bayes")

    item_it = c.execute("SELECT Items.*, Feeds.Language FROM Items INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE Items.ItemID=?", (qd['id'], )).fetchone()
    title = item_it['Title']
    summary = item_it['Summary']

    pipeline = scorers[item_it['Language']]
    count_vect = pipeline.named_steps['vect']
    analyzer = count_vect.build_analyzer()
    preprocessor = count_vect.build_preprocessor()
    tokenizer = count_vect.build_tokenizer()

    table = list(count_vect.vocabulary_.keys())
    coeffs = pipeline.predict_proba(table)
    coeffs = 2. * coeffs - 1.
    table = dict([(table[i], coeffs[i, 1], ) for i in range(len(table))])

    coeffs_sort = sorted(coeffs[:, 1])
    coeff_dislike = coeffs_sort[20]
    coeff_like = coeffs_sort[-20]

    new_title = ""
    idx_left = 0
    while True:
        idx_right = title.find("<", idx_left)
        section = title[idx_left:idx_right]
        if idx_right == -1:
            section = title[idx_left:]

        for token_it in set(tokenizer(section)):
            try:
                coeff = table[preprocessor(token_it)]
            except KeyError:
                continue
            if coeff < coeff_dislike or coeff >= coeff_like:
                section = section.replace(token_it, "<mark>{}</mark>".format(token_it))
        new_title += section

        if idx_right == -1:
            break
        else:
            idx_left = title.find(">", idx_right) + 1
            new_title += title[idx_right:idx_left]

    new_summary = ""
    idx_left = 0
    while True:
        idx_right = summary.find("<", idx_left)
        section = summary[idx_left:idx_right]
        if idx_right == -1:
            section = summary[idx_left:]

        for token_it in set(tokenizer(section)):
            try:
                coeff = table[preprocessor(token_it)]
            except KeyError:
                continue
            if coeff < coeff_dislike or coeff >= coeff_like:
                section = section.replace(token_it, "<mark>{}</mark>".format(token_it))
        new_summary += section

        if idx_right == -1:
            break
        else:
            idx_left = summary.find(">", idx_right) + 1
            new_summary += summary[idx_right:idx_left]

    return new_title + chr(0) + new_summary

if __name__ == "__main__":
    clfs = steins_learn("hansolo", "Logistic Regression")
    clf = clfs['English']
    count_vect = clf.named_steps['vect']
    tfidf_transformer = clf.named_steps['tfidf']
    lr_clf = clf.named_steps['clf']
    table = count_vect.vocabulary_.items()
    coeffs = lr_clf.coef_[0] * tfidf_transformer.idf_
    table = [row + (coeffs[row[1]], ) for row in table]
    table = sorted(table, key=lambda row: row[2])
    print("Least favorite:", [row[0] for row in table[:10]])
    print("Most favorite:", [row[0] for row in reversed(table[-10:])])
