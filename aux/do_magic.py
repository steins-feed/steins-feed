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
from steins_magic import build_feature, clf_dict, kullback_leibler, steins_learn
from steins_sql import get_connection, last_updated, last_liked, reset_magic
conn = get_connection()
c = conn.cursor()

users = c.execute("SELECT * FROM Users").fetchall()
for user_it in users:
    user = user_it['Name']
    user_id = user_it['UserID']

    user_path = dir_path + os.sep + str(user_id)
    try:
        os.mkdir(user_path)
    except FileExistsError:
        pass

    timestamp = last_updated()
    timestamp_like = last_liked(user_id)

    for clf_it in clf_dict:
        clf_path = user_path + os.sep + clf_it
        try:
            os.mkdir(clf_path)
        except FileExistsError:
            pass

        file_path = clf_path + os.sep + "clfs.pickle"
        if os.path.exists(file_path) and datetime.fromtimestamp(os.stat(file_path).st_mtime) > timestamp_like:
            with open(file_path, 'rb') as f:
                clfs = pickle.load(f)
        else:
            clfs = steins_learn(user_id, clf_it)
            reset_magic(user_id, clf_it)
            with open(file_path, 'wb') as f:
                pickle.dump(clfs, f)
                logger.info("Learn {} about {}.".format(clf_it, user))

        for lang_it in clfs:
            pipeline = clfs[lang_it]
            count_vect = pipeline.named_steps['vect']

            # Words.
            #words = list(count_vect.vocabulary_.keys())
            words = list(count_vect.vocabulary_nltk.values())
            coeffs = pipeline.predict_proba(words)
            coeffs = coeffs[:, 1]
            table = dict(zip(words, coeffs))

            # If KL divergence below threshold, do not prepare analysis.
            try:
                file_path = clf_path + os.sep + "{}.pickle".format(lang_it)
                with open(file_path, 'rb') as f:
                    table_old = pickle.load(f)
                    div = kullback_leibler(table, table_old)
                    logger.info("Kullback-Leibler divergence of {}, {}, {}: {}.".format(user, clf_it, lang_it, div))

                    if abs(div) < 0.5:
                        continue
            except FileNotFoundError:
                pass

            with open(file_path, 'wb') as f:
                pickle.dump(table, f)
                logger.info("Learn {} about {} ({} words).".format(clf_it, user, lang_it))

            # Feeds.
            feeds = [row['FeedID'] for row in c.execute("SELECT FeedID FROM Feeds INNER JOIN Display USING (FeedID) WHERE UserID=? AND Language=?", (user_id, lang_it, ))]

            coeffs = []
            for feed_id in feeds:
                articles_raw = c.execute("SELECT * FROM (Items INNER JOIN Feeds USING (FeedID)) INNER JOIN Display USING (FeedID) WHERE FeedID=? AND Published<?", (feed_id, timestamp, )).fetchall()
                articles = [build_feature(row) for row in articles_raw]

                if len(articles) == 0:
                    coeffs.append(0.5)
                    continue

                articles_proba = pipeline.predict_proba(articles)
                articles_proba = articles_proba[:, 1]
                for i in range(len(articles)):
                    c.execute("INSERT OR IGNORE INTO {} (UserID, ItemID, Score) VALUES (?, ?, ?)".format(clf_dict[clf_it]['table']), (user_id, articles_raw[i]['ItemID'], articles_proba[i], ))
                conn.commit()

                articles_proba = articles_proba / (1. - articles_proba)
                articles_proba = np.log(articles_proba)
                coeff = np.sum(articles_proba) / (articles_proba.size + 10.)
                coeffs.append(coeff)

            coeffs = np.exp(coeffs)
            coeffs = coeffs / (1. + coeffs)
            table = dict(zip(feeds, coeffs))

            file_path = clf_path + os.sep + "{}_feeds.pickle".format(lang_it)
            with open(file_path, 'wb') as f:
                pickle.dump(table, f)
                logger.info("Learn {} about {} ({} feeds).".format(clf_it, user, lang_it))

conn.close()
