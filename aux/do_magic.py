#!/usr/bin/env python3

from collections import OrderedDict
from datetime import datetime, timedelta
import json
import numpy as np
import os
import pickle
import sqlalchemy as sqla
import sys

def mkdir_p(s):
    try:
        os.mkdir(s)
    except FileExistsError:
        pass

par_path = os.path.normpath(os.path.join(
    os.path.dirname(__file__),
    os.pardir
))
sys.path.append(par_path)
dir_path = os.path.join(par_path, "clf.d")
mkdir_p(dir_path)

from magic import train_classifier
from model import get_connection, get_table
from model import get_session
from model.orm import feeds as orm_feeds, items as orm_items
from model.schema.feeds import Language
from model.schema.items import Like
from model.utils import last_updated, last_liked
from model.utils.custom import reset_magic

def liked_languages(user_id):
    q = sqla.select(
        orm_feeds.Feed.Language
    ).select_from(
        orm_items.Like
    ).join(
        orm_items.Like.item
    ).join(
        orm_items.Item.feed
    ).where(
        orm_items.Like.UserID == user_id,
        orm_items.Like.Score != Like.MEH.name,
    ).distinct()

    with get_session() as session:
        return [Language[e["Language"]] for e in session.execute(q)]

def liked_items(user_id, lang, score=Like.UP):
    q = sqla.select(
        orm_items.Item
    ).where(
        orm_items.Item.feed.has(
            orm_feeds.Feed.Language == lang.name
        ),
        orm_items.Item.likes.any(sqla.and_(
            orm_items.Like.UserID == user_id,
            orm_items.Like.Score == score.name,
        )),
    )

    with get_session() as session:
        return [e[0] for e in session.execute(q)]

def disliked_items(user_id, lang):
    return liked_items(user_id, lang, Like.DOWN)

def do_words(pipeline):
    count_vect = pipeline.named_steps['vect']

    words = list(count_vect.vocabulary_nltk.values())
    coeffs = pipeline.predict_proba(words)[:, 1]
    table = zip(words, coeffs)
    table = sorted(table, key=lambda x: x[1])
    table = OrderedDict(table)

    return table

def do_cookies(pipeline):
    count_vect = pipeline.named_steps['vect']

    words = list(count_vect.vocabulary_nltk.keys())
    coeffs = pipeline.predict_proba(words)[:, 1]
    table = zip(words, coeffs)
    table = sorted(table, key=lambda x: x[1])
    table = OrderedDict(table)

    return table

def do_feeds(pipeline, user_id, lang, timestamp, delta_timestamp=timedelta(days=100)):
    feeds = c.execute("SELECT * FROM Feeds INNER JOIN Display USING (FeedID) WHERE UserID=? AND Language=?", (user_id, lang, )).fetchall()
    coeffs = []

    for feed_it in feeds:
        articles_raw = c.execute("SELECT * FROM (Items INNER JOIN Feeds USING (FeedID)) INNER JOIN Display USING (FeedID) WHERE FeedID=? AND Published BETWEEN ? AND ?", (feed_it['FeedID'], timestamp - delta_timestamp, timestamp, )).fetchall()
        articles = [build_feature(row) for row in articles_raw]

        if len(articles) == 0:
            coeffs.append(0.5)
            continue

        articles_proba = pipeline.predict_proba(articles)[:, 1]
        for i in range(len(articles)):
            c.execute("INSERT OR IGNORE INTO {} (UserID, ItemID, Score) VALUES (?, ?, ?)".format(clf_dict[clf_it]['table']), (user_id, articles_raw[i]['ItemID'], articles_proba[i], ))
            logger.debug("Score item -- {} ({}).".format(articles_raw[i]['Title'], 2. * articles_proba[i] - 1.))
        conn.commit()

        articles_proba /= (1. - articles_proba)
        articles_proba = np.log(articles_proba)
        coeff = np.sum(articles_proba) / (articles_proba.size + 10.)
        coeff = np.exp(coeff)
        coeff /= (1. + coeff)

        logger.debug("Score feed -- {} ({}).".format(feed_it['Title'], 2. * coeff - 1.))
        coeffs.append(coeff)

    feed_ids = [e['FeedID'] for e in feeds]
    table = zip(feed_ids, coeffs)
    table = sorted(table, key=lambda x: x[1])
    table = OrderedDict(table)

    return table

with get_connection() as conn:
    users = conn.execute(sqla.select(get_table("Users"))).fetchall()

for user_it in users:
    user = user_it.Name
    user_id = user_it.UserID
    user_path = os.path.join(dir_path, str(user_id))
    mkdir_p(user_path)

    timestamp = last_updated()
    timestamp_like = last_liked(user_id)

    for lang_it in liked_languages(user_id):
        file_path = os.path.join(user_path, lang_it.name + ".pickle")
        if os.path.exists(file_path) and datetime.utcfromtimestamp(os.stat(file_path).st_mtime) > timestamp_like:
            with open(file_path, 'rb') as f:
                clf = pickle.load(f)
        else:
            #logger.info("Learn {} about {}.".format(lang_it.name, user))
            likes = liked_items(user_id, lang_it)
            dislikes = disliked_items(user_id, lang_it)
            clf = train_classifier(user_id, lang_it, likes, dislikes)
            if not clf:
                continue
            reset_magic(user_id, lang_it)
            with open(file_path, 'wb') as f:
                pickle.dump(clf, f)

    #for lang_it in clfs:
    #    # Words.
    #    table = do_words(clfs[lang_it])

    #    # If KL divergence below threshold, do not prepare analysis.
    #    try:
    #        file_path = clf_path + os.sep + "{}_words.json".format(lang_it)
    #        with open(file_path, 'r') as f:
    #            table_old = json.load(f)
    #            div = kullback_leibler(table, table_old)
    #            logger.info("Kullback-Leibler divergence of {}, {}, {}: {}.".format(user, clf_it, lang_it, div))

    #            if abs(div) < 0.5:
    #                continue
    #    except FileNotFoundError:
    #        pass

    #    logger.info("Learn {} about {} ({} words).".format(clf_it, user, lang_it))
    #    with open(file_path, 'w') as f:
    #        json.dump(table, f)

    #    # Cookies.
    #    logger.info("Learn {} about {} ({} cookies).".format(clf_it, user, lang_it))
    #    file_path = clf_path + os.sep + "{}_cookie.json".format(lang_it)
    #    with open(file_path, 'w') as f:
    #        table = do_cookies(clfs[lang_it])
    #        json.dump(table, f)

    #    # Feeds.
    #    logger.info("Learn {} about {} ({} feeds).".format(clf_it, user, lang_it))
    #    file_path = clf_path + os.sep + "{}_feeds.json".format(lang_it)
    #    with open(file_path, 'w') as f:
    #        table = do_feeds(clfs[lang_it], user_id, lang_it, timestamp)
    #        json.dump(table, f)
