#!/usr/bin/env python3

from lxml.html import tostring, builder as E
import os
import pickle
import re

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline

from steins_html import decode, preamble, side_nav, top_nav, unescape
from steins_nltk import NLTK_CountVectorizer
from steins_sql import *

dir_path = os.path.dirname(os.path.abspath(__file__))

no_words = 20
no_feeds = 10
no_articles = 100

def build_feature(row):
    title = row['Title'] + " " + row['Summary']
    idx1 = title.find("<")
    while not idx1 == -1:
        idx2 = title.find(">", idx1)
        if idx2 == -1:
            break
        title = title[:idx1] + title[idx2+1:]
        idx1 = title.find("<")
    return unescape(title)

def steins_learn(user, classifier):
    c = get_cursor()
    user_id = get_user_id(user)
    timestamp = last_updated()

    clfs = dict()
    langs = [e[0] for e in c.execute("SELECT DISTINCT Feeds.Language FROM (Items INNER JOIN Feeds ON Items.FeedID=Feeds.FeedID) INNER JOIN Like ON Items.ItemID=Like.ItemID WHERE UserID=? AND Published<? AND Score!=0", (user_id, timestamp, ))]

    for lang_it in langs:
        likes = c.execute("SELECT Items.* FROM (Items INNER JOIN Feeds ON Items.FeedID=Feeds.FeedID) INNER JOIN Like ON Items.ItemID=Like.ItemID WHERE UserID=? AND Language=? AND Published<? AND Score=1", (user_id, lang_it, timestamp, )).fetchall()
        dislikes = c.execute("SELECT Items.* FROM (Items INNER JOIN Feeds ON Items.FeedID=Feeds.FeedID) INNER JOIN Like ON Items.ItemID=Like.ItemID WHERE UserID=? AND Language=? AND Published<? AND Score=-1", (user_id, lang_it, timestamp, )).fetchall()
        if len(likes) == 0 or len(dislikes) == 0:
            continue

        titles = []
        titles += [build_feature(row_it) for row_it in likes]
        titles += [build_feature(row_it) for row_it in dislikes]

        targets = []
        targets += [1 for row_it in likes]
        targets += [-1 for row_it in dislikes]

        # Build pipeline.
        #count_vect = ('vect', CountVectorizer())
        count_vect = ('vect', NLTK_CountVectorizer(lang_it))
        tfidf_transformer = ('tfidf', TfidfTransformer())

        if classifier == 'NaiveBayes':
            clf = ('clf', MultinomialNB())
        elif classifier == 'LogisticRegression':
            clf = ('clf', LogisticRegression())
        #elif classifier == 'SVM':
        #    clf = ('clf', SVC(probability=True))
        #elif classifier == 'Linear SVM':
        #    clf = ('clf', SVC(kernel='linear', probability=True))
        else:
            raise KeyError
        text_clf = Pipeline([count_vect, tfidf_transformer, clf])

        # Train classifier.
        try:
            clf = text_clf.fit(titles, targets)
        except ValueError:
            continue
        clfs[lang_it] = clf

    return clfs

def handle_analysis(qd):
    user = qd['user']
    clf = qd['clf']
    timestamp = last_updated()

    user_path = dir_path + os.sep + user
    clf_path = user_path + os.sep + clf
    with open(clf_path + os.sep + "clfs.pickle", 'rb') as f:
        clfs = pickle.load(f)
    langs = clfs.keys()

    #--------------------------------------------------------------------------

    # Preamble.
    tree, head, body = preamble(user)

    #--------------------------------------------------------------------------

    # Scripts.
    for js_it in ["open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js"]:
        script_it = E.SCRIPT()
        with open(dir_path + os.sep + "js" + os.sep + js_it, 'r') as f:
            script_it.text = f.read()
        head.append(script_it)

    #--------------------------------------------------------------------------

    # Top & side navigation menus.
    body.append(top_nav(user))
    body.append(side_nav(user))

    #--------------------------------------------------------------------------

    # Body.
    div_it = E.DIV(E.CLASS("main"))
    body.append(div_it)
    p_it = E.P()
    div_it.append(p_it)
    p_it.text = "Last updated: {}.".format(timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"))
    div_it.append(E.HR())

    #--------------------------------------------------------------------------

    tables = dict()
    for lang_it in langs:
        with open(clf_path + os.sep + "{}.pickle".format(lang_it), 'rb') as f:
            tables[lang_it] = pickle.load(f)

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

    for i in reversed(range(-no_words, 0)):
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

    for i in range(no_words):
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
        with open(clf_path + os.sep + "{}_feeds.pickle".format(lang_it), 'rb') as f:
            tables[lang_it] = pickle.load(f)

    # Most favorite feeds.
    h_it = E.H2()
    h_it.text = "Most recommended feeds"
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

    for i in reversed(range(-no_feeds, 0)):
        tr_it = E.TR()
        for lang_it in langs:
            td_it = E.TD()
            try:
                td_it.text = "{} ({:.2f})".format(tables[lang_it][i][0], tables[lang_it][i][1])
            except IndexError:
                td_it.text = "-"
            tr_it.append(td_it)
        table_it.append(tr_it)

    # Least favorite feeds.
    h_it = E.H2()
    h_it.text = "Least recommended feeds"
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

    for i in range(no_feeds):
        tr_it = E.TR()
        for lang_it in langs:
            td_it = E.TD()
            try:
                td_it.text = "{} ({:.2f})".format(tables[lang_it][i][0], tables[lang_it][i][1])
            except IndexError:
                td_it.text = "-"
            tr_it.append(td_it)
        table_it.append(tr_it)

    #--------------------------------------------------------------------------

    return decode(tostring(tree, doctype="<!DOCTYPE html>", pretty_print=True))

def handle_highlight(qd):
    c = get_cursor()

    user = qd['user']
    clf = qd['clf']
    item_id = int(qd['id'])

    user_path = dir_path + os.sep + user
    clf_path = user_path + os.sep + clf
    with open(clf_path + os.sep + "clfs.pickle", 'rb') as f:
        clfs = pickle.load(f)

    item_it = c.execute("SELECT Items.*, Feeds.Language FROM Items INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE Items.ItemID=?", (item_id, )).fetchone()
    title = "<span>" + unescape(item_it['Title']) + "</span>"
    summary = "<div>" + unescape(item_it['Summary']) + "</div>"

    clf = clfs[item_it['Language']]
    count_vect = clf.named_steps['vect']
    analyzer = count_vect.build_analyzer()
    #preprocessor = count_vect.build_preprocessor()
    tokenizer = count_vect.build_tokenizer()

    #coeff_dislike = -0.5
    #coeff_like = 0.5
    with open(clf_path + os.sep + "{}.pickle".format(item_it['Language']), 'rb') as f:
        table = pickle.load(f)
    coeff_dislike = table[no_words][1]
    coeff_like = table[-no_words][1]

    new_title = ""
    idx_left = 0
    while True:
        idx_right = title.find("<", idx_left)
        section = title[idx_left:idx_right]
        if idx_right == -1:
            section = title[idx_left:]

        for token_it in set(tokenizer(section)):
            expr = " ".join(analyzer(token_it))
            coeff = 2. * clf.predict_proba([expr])[0][1] - 1.
            if coeff < coeff_dislike or coeff >= coeff_like:
                section = re.sub(r"\b{}\b".format(token_it), "<span class=\"tooltip\"><mark>{}</mark><span class=\"tooltiptext\">{:.2f}</span></span>".format(token_it, coeff), section)
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
            expr = " ".join(analyzer(token_it))
            coeff = 2. * clf.predict_proba([expr])[0][1] - 1.
            if coeff < coeff_dislike or coeff >= coeff_like:
                section = re.sub(r"\b{}\b".format(token_it), "<span class=\"tooltip\"><mark>{}</mark><span class=\"tooltiptext\">{:.2f}</span></span>".format(token_it, coeff), section)
        new_summary += section

        if idx_right == -1:
            break
        else:
            idx_left = summary.find(">", idx_right) + 1
            new_summary += summary[idx_right:idx_left]

    return new_title + chr(0) + new_summary
