#!/usr/bin/env python3

from datetime import datetime
from lxml.html import tostring, builder as E
import numpy as np
import numpy.random as random
import os
import pickle
import time
from urllib.parse import urlparse

from steins_html import decode, feed_node, preamble, side_nav, top_nav
from steins_log import get_logger
from steins_magic import build_feature
from steins_manager import get_handler
from steins_sql import add_item, get_cursor, last_update, last_updated

dir_path = os.path.dirname(os.path.abspath(__file__))

no_surprise = 10

# Scrape feeds.
def steins_read(title_pattern=""):
    c = get_cursor()
    logger = get_logger()

    for feed_it in c.execute("SELECT * FROM Feeds WHERE Title LIKE ?", ("%" + title_pattern + "%", )).fetchall():
        handler = get_handler(feed_it['Title'])
        d = handler.parse(feed_it['Link'])
        try:
            logger.info("{} -- {}.".format(feed_it['Title'], d.status))
        except AttributeError:
            logger.info("{}.".format(feed_it['Title']))

        for item_it in d['items']:
            try:
                item_title = handler.read_title(item_it)
                item_time = handler.read_time(item_it)
                item_summary = handler.read_summary(item_it)
                item_link = handler.read_link(item_it)
            except KeyError:
                continue

            add_item(item_title, item_time, item_summary, feed_it['Title'], item_link)

def handle_page(qd):
    c = get_cursor()
    timestamp = last_updated()

    user = qd['user']
    lang = qd['lang']
    page_no = int(qd['page'])
    feed = qd['feed']
    clf = qd['clf']

    # Classifier.
    clfs = []
    if not feed == "Full":
        user_path = dir_path + os.sep + user
        clf_path = user_path + os.sep + clf
        with open(clf_path + os.sep + "clfs.pickle", 'rb') as f:
            clfs = pickle.load(f)

    # Surprise.
    surprise = -1
    if feed == "Surprise":
        surprise = no_surprise

    # Language.
    if lang == "International":
        dates = c.execute(
            "WITH Titles AS (SELECT Feeds.*, Display.{0} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID),"
            "Sources AS (SELECT Title FROM Titles WHERE {0}=1)"
            "SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN Sources AND Published<? ORDER BY Published DESC"
            .format(user),
            (timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"), )
        ).fetchall()
    else:
        dates = c.execute(
            "WITH Titles AS (SELECT Feeds.*, Display.{0} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID),"
            "Sources AS (SELECT Title FROM Titles WHERE {0}=1 AND Language=?)"
            "SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN Sources AND Published<? ORDER BY Published DESC"
            .format(user),
            (lang, timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"), )
        ).fetchall()
    if page_no >= len(dates):
        return
    d_it = dates[page_no][0]
    if lang == "International":
        items = c.execute(
            "WITH Titles AS (SELECT Feeds.*, Display.{0} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID),"
            "Sources AS (SELECT Title FROM Titles WHERE {0}=1)"
            "SELECT Items.*, Like.{0} AS Like, Feeds.Language FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE Source IN Sources AND SUBSTR(Published, 1, 10)=? AND Published<? ORDER BY Published DESC"
            .format(user),
            (d_it, timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"), )
        ).fetchall()
    else:
        items = c.execute(
            "With Titles AS (SELECT Feeds.*, Display.{0} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID),"
            "Sources AS (SELECT Title FROM Titles WHERE {0}=1 AND Language=?)"
            "SELECT Items.*, Like.{0} AS Like, Feeds.Language FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE Source IN Sources AND SUBSTR(Published, 1, 10)=? AND Published<? ORDER BY Published DESC"
            .format(user),
            (lang, d_it, timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"), )
        ).fetchall()

    # Remove duplicates.
    item_links = set()
    items_unique = []
    for item_it in reversed(items):
        item_link = urlparse(item_it['Link'])
        item_link = item_link._replace(params='', query='', fragment='')
        if item_link in item_links:
            continue
        item_links.add(item_link)
        items_unique.append(item_it)
    items = list(reversed(items_unique))

    #--------------------------------------------------------------------------

    # Preamble.
    tree, head, body = preamble("Stein's Feed")

    #--------------------------------------------------------------------------

    # Scripts.
    for js_it in ["like.js", "dislike.js", "highlight.js", "open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js"]:
        script_it = E.SCRIPT()
        with open(dir_path + os.sep + "js" + os.sep + js_it, 'r') as f:
            f_temp = f.read()
            f_temp = f_temp.replace("USER", user)
            f_temp = f_temp.replace("CLF", clf.replace(" ", "+"))
            script_it.text = f_temp
        head.append(script_it)

    #--------------------------------------------------------------------------

    # Top & side navigation menus.
    body.append(top_nav(time.strftime("%A, %d %B %Y", time.strptime(d_it, "%Y-%m-%d"))))
    body.append(side_nav(user, lang, page_no, feed, clf, dates))

    #--------------------------------------------------------------------------

    # Body.
    div_it = E.DIV(E.CLASS("main"))
    body.append(div_it)

    p_it = E.P()
    div_it.append(p_it)
    if surprise > 0:
        p_it.text = "{} out of {} articles. {} pages. Last updated: {}.".format(surprise, len(items), len(dates), timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"))
    else:
        p_it.text = "{} articles. {} pages. Last updated: {}.\n".format(len(items), len(dates), timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"))

    # Classifier.
    if len(clfs) != 0:
        scores = np.zeros(len(items))
        langs = set([e['Language'] for e in items])

        for lang_it in langs:
            try:
                clf = clfs[lang_it]
            except KeyError:
                continue

            idx = [i for i in range(len(items)) if items[i]['Language'] == lang_it]
            new_titles = [build_feature(items[i]) for i in idx]
            predicted_proba = clf.predict_proba(new_titles)
            scores[idx] = [it[1] - it[0] for it in predicted_proba]

        for item_ct in range(len(items)):
            items[item_ct] = dict(items[item_ct])
            items[item_ct]['Score'] = scores[item_ct]

    # Surprise.
    if surprise > 0:
        logit_scores = np.log((1. + scores) / (1. - scores))
        sigma = np.sqrt(np.sum(logit_scores**2) / scores.size)
        probs = np.exp(-0.5 * logit_scores**2 / sigma**2) * (1. / (1. + scores) + 1. / (1. - scores)) / sigma / np.sqrt(2. * np.pi)
        probs /= np.sum(probs)
        sample = random.choice(scores.size, surprise, False, probs)
        items = [items[cnt] for cnt in sample]
    elif len(clfs) != 0:
        items.sort(key=lambda item_it: item_it['Score'], reverse=True)

    for item_it in items:
        div_it.append(E.HR())
        div_it.append(feed_node(item_it))

    return decode(tostring(tree, doctype="<!DOCTYPE html>", pretty_print=True))

# Generate HTML.
def steins_write():
    c = get_cursor()

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items ORDER BY Published DESC").fetchall()
    for d_ctr in range(len(dates)):
        with open(dir_path+os.sep+"steins-{}.html".format(d_ctr), 'w') as f:
            f.write(handle_page(page=d_ctr))

def steins_update(title_pattern="", read_mode=True, write_mode=False):
    #last_update()
    if read_mode:
        record = datetime.utcnow()
        steins_read(title_pattern)
        last_update(record)
    if write_mode:
        steins_write()

if __name__ == "__main__":
    import sys
    from steins_sql import close_connection

    title_pattern = ""
    if len(sys.argv) > 1:
        title_pattern = sys.argv[1]
    steins_update(title_pattern)
    close_connection()
