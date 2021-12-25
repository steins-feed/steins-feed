#!/usr/bin/env python3

"""Retrains classifiers."""

import collections
import logging
import os
import sklearn
import sqlalchemy as sqla
import sys

from util import is_up_to_date, mkdir_p

par_path = os.path.join(
    os.path.dirname(__file__),
    os.pardir,
)
sys.path.append(par_path)

import log
import magic
from magic import io as magic_io
import model
from model import liked, recent
from model.orm import users as orm_users
from model.schema import feeds as schema_feeds

logger = log.Logger(__name__, logging.INFO)

def reset_magic(
    user_id: int = None,
    lang: schema_feeds.Language = None,
):
    """
    Resets magic.

    Args:
      user_id: User ID.
      lang: Language.
    """
    feeds = model.get_table('Feeds')
    items = model.get_table('Items')
    magic = model.get_table('Magic')

    q = magic.delete()

    if user_id:
        q = q.where(magic.c.UserID == user_id)

    if lang:
        if user_id:
            q_cte = sqla.select(
                items.c.ItemID,
            ).select_from(
                items.join(feeds)
                     .join(magic)
            ).where(
                feeds.c.Language == lang.name,
                magic.c.UserID == user_id,
            ).distinct()
        else:
            q_cte = sqla.select(
                items.c.ItemID,
            ).select_from(
                items.join(feeds)
            ).where(
                feeds.c.Language == lang.name,
            ).distinct()

        q = q.where(magic.c.ItemID.in_(q_cte))

    with model.get_connection() as conn:
        conn.execute(q)

def do_words(pipeline: sklearn.pipeline.Pipeline) -> dict[str, float]:
    """
    Likelihoods of liking words.

    Args:
      pipeline: Scikit-learn pipeline.

    Returns:
      Words and their scores.
    """
    count_vect = pipeline.named_steps['vect']

    words = list(count_vect.vocabulary_nltk.values())
    coeffs = pipeline.predict_proba(words)[:, 1]
    table = zip(words, coeffs)
    table = sorted(table, key=lambda x: x[1])
    table = collections.OrderedDict(table)

    return table

def do_cookies(pipeline: sklearn.pipeline.Pipeline) -> dict[str, float]:
    """
    Likelihoods of liking words.

    Args:
      pipeline: Scikit-learn pipeline.

    Returns:
      Words and their scores.
    """
    count_vect = pipeline.named_steps['vect']

    words = list(count_vect.vocabulary_nltk.keys())
    coeffs = pipeline.predict_proba(words)[:, 1]
    table = zip(words, coeffs)
    table = sorted(table, key=lambda x: x[1])
    table = OrderedDict(table)

    return table

#def do_feeds(pipeline, user_id, lang, timestamp, delta_timestamp=timedelta(days=100)):
#    feeds = c.execute("SELECT * FROM Feeds INNER JOIN Display USING (FeedID) WHERE UserID=? AND Language=?", (user_id, lang, )).fetchall()
#    coeffs = []
#
#    for feed_it in feeds:
#        articles_raw = c.execute("SELECT * FROM (Items INNER JOIN Feeds USING (FeedID)) INNER JOIN Display USING (FeedID) WHERE FeedID=? AND Published BETWEEN ? AND ?", (feed_it['FeedID'], timestamp - delta_timestamp, timestamp, )).fetchall()
#        articles = [build_feature(row) for row in articles_raw]
#
#        if len(articles) == 0:
#            coeffs.append(0.5)
#            continue
#
#        articles_proba = pipeline.predict_proba(articles)[:, 1]
#        for i in range(len(articles)):
#            c.execute("INSERT OR IGNORE INTO {} (UserID, ItemID, Score) VALUES (?, ?, ?)".format(clf_dict[clf_it]['table']), (user_id, articles_raw[i]['ItemID'], articles_proba[i], ))
#            logger.debug("Score item -- {} ({}).".format(articles_raw[i]['Title'], 2. * articles_proba[i] - 1.))
#        conn.commit()
#
#        articles_proba /= (1. - articles_proba)
#        articles_proba = np.log(articles_proba)
#        coeff = np.sum(articles_proba) / (articles_proba.size + 10.)
#        coeff = np.exp(coeff)
#        coeff /= (1. + coeff)
#
#        logger.debug("Score feed -- {} ({}).".format(feed_it['Title'], 2. * coeff - 1.))
#        coeffs.append(coeff)
#
#    feed_ids = [e['FeedID'] for e in feeds]
#    table = zip(feed_ids, coeffs)
#    table = sorted(table, key=lambda x: x[1])
#    table = OrderedDict(table)
#
#    return table

if __name__ == "__main__":
    dir_path = os.path.join(
        par_path,
        "clf.d",
    )
    mkdir_p(dir_path)

    with model.get_session() as session:
        users = [e[0] for e in session.execute(sqla.select(orm_users.User))]

    for user_it in users:
        user_path = os.path.join(
            dir_path,
            str(user_it.UserID),
        )
        mkdir_p(user_path)

        datetime_like = recent.last_liked(user_it.UserID)

        for lang_it in liked.liked_languages(user_it.UserID):
            file_path = os.path.join(
                user_path,
                lang_it.name + ".pickle",
            )
            if is_up_to_date(file_path, datetime_like):
                clf = magic_io.read_classifier(user_it, lang_it)
            else:
                logger.info(f"Learn {lang_it.name} about {user_it.Name}.")

                likes = liked.liked_items(user_it.UserID, lang_it)
                dislikes = liked.disliked_items(user_it.UserID, lang_it)
                clf = magic.train_classifier(user_it.UserID, lang_it, likes, dislikes)

                reset_magic(user_it.UserID, lang_it)
                magic_io.write_classifier(clf, user_it, lang_it)

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
