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
from steins_magic import build_feature, steins_learn
from steins_sql import get_cursor, last_updated

c = get_cursor()
logger = get_logger()
timestamp = last_updated()

users = [e[0] for e in c.execute("SELECT Name FROM Users").fetchall()]
for user_it in users:
    user_path = dir_path + os.sep + user_it
    try:
        os.mkdir(user_path)
    except FileExistsError:
        pass

    #for clf_it in ["Naive Bayes", "Logistic Regression", "SVM", "Linear SVM"]:
    for clf_it in ["Naive Bayes", "Logistic Regression"]:
        clf_path = user_path + os.sep + clf_it
        try:
            os.mkdir(clf_path)
        except FileExistsError:
            pass

        clfs = steins_learn(user_it, clf_it)
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
            with open(clf_path + os.sep + "{}.pickle".format(lang_it), 'wb') as f:
                pickle.dump(sorted(table, key=lambda row: row[1]), f)
                logger.info("Learn {} about {} ({} words).".format(clf_it, user_it, lang_it))

            # Feeds.
            feeds = [row[0] for row in c.execute("SELECT Title FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE Language=? AND Display.{}=1".format(user_it), (lang_it, )).fetchall()]
            coeffs = []
            for title_it in feeds:
                articles = [build_feature(row) for row in c.execute("SELECT * FROM Items WHERE Source=? AND Published<? ORDER BY Published DESC", (title_it, timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"), )).fetchall()]
                #articles = [build_feature(row) for row in c.execute("SELECT * FROM Items WHERE Source=? AND Published<? ORDER BY Published DESC LIMIT ?", (title_it, timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"), no_articles, )).fetchall()]
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