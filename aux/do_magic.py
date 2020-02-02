#!/usr/bin/env python3

import numpy as np
import os
import pickle
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_log import get_logger
logger = get_logger()
from steins_magic import build_feature, steins_learn
from steins_sql import *
c = get_cursor()

def kullback_leibler(q, p):
    ev_q = 0.
    for k in q:
        q[k] = 0.5 * (1. + q[k])
        ev_q += q[k]

    ev_p = 0.
    for k in p:
        p[k] = 0.5 * (1. + p[k])
        ev_p += p[k]

    res = 0.
    for k in p:
        if k not in q:
            continue
        q[k] /= ev_q
        p[k] /= ev_p
        res += p[k] * np.log(p[k] / q[k])

    return res

users = [e[0] for e in c.execute("SELECT Name FROM Users")]
for user_it in users:
    user_path = dir_path + os.sep + user_it
    try:
        os.mkdir(user_path)
    except FileExistsError:
        pass

    user_id = get_user_id(user_it)
    timestamp = last_updated()
    timestamp_like = last_liked(user_id)

    for clf_it in ["NaiveBayes", "LogisticRegression"]:
        clf_path = user_path + os.sep + clf_it
        try:
            os.mkdir(clf_path)
        except FileExistsError:
            pass

        file_path = clf_path + os.sep + "clfs.pickle"
        if os.path.exists(file_path) and datetime.fromtimestamp(os.stat(file_path).st_mtime) < timestamp_like:
            with open(clf_path + os.sep + "clfs.pickle", 'rb') as f:
                clfs = pickle.load(f)
        else:
            clfs = steins_learn(user_it, clf_it)
            reset_magic(user_it, clf_it)
            with open(clf_path + os.sep + "clfs.pickle", 'wb') as f:
                pickle.dump(clfs, f)
                logger.info("Learn {} about {}.".format(clf_it, user_it))

        for lang_it in clfs.keys():
            pipeline = clfs[lang_it]
            count_vect = pipeline.named_steps['vect']

            # Words.
            #table = list(count_vect.vocabulary_.keys())
            table = list(count_vect.vocabulary_nltk.values())
            coeffs = pipeline.predict_proba(table)
            coeffs = 2. * coeffs - 1.
            table = [(table[i], coeffs[i, 1], ) for i in range(len(table))]

            try:
                with open(clf_path + os.sep + "{}.pickle".format(lang_it), 'rb') as f:
                    table_old = pickle.load(f)
                    div = kullback_leibler(dict(table), dict(table_old))
                    logger.info("Kullback-Leibler divergence of {}, {}, {}: {}.".format(user_it, clf_it, lang_it, div))
                    if abs(div) < 0.5:
                        continue
            except FileNotFoundError:
                pass

            with open(clf_path + os.sep + "{}.pickle".format(lang_it), 'wb') as f:
                pickle.dump(sorted(table, key=lambda row: row[1]), f)
                logger.info("Learn {} about {} ({} words).".format(clf_it, user_it, lang_it))

            # Feeds.
            feeds = [row[0] for row in c.execute("SELECT Title FROM Feeds INNER JOIN Display ON Feeds.FeedID=Display.FeedID WHERE Language=? AND UserID=?", (lang_it, user_id, ))]
            coeffs = []
            for title_it in feeds:
                articles = [build_feature(row) for row in c.execute("SELECT * FROM Items WHERE FeedID=(SELECT FeedID FROM Feeds WHERE Title=?) AND Published<?", (title_it, timestamp, ))]
                #articles = [build_feature(row) for row in c.execute("SELECT * FROM Items WHERE Source=? AND Published<? ORDER BY Published DESC LIMIT ?", (title_it, timestamp, no_articles, ))]
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
            with open(clf_path + os.sep + "{}_feeds.pickle".format(lang_it), 'wb') as f:
                pickle.dump(sorted(table, key=lambda row: row[1]), f)
                logger.info("Learn {} about {} ({} feeds).".format(clf_it, user_it, lang_it))
