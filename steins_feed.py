#!/usr/bin/env python3

import os
dir_path = os.path.dirname(os.path.abspath(__file__))

from steins_log import get_logger
logger = get_logger()
from steins_manager import get_handler
from steins_sql import *

no_surprise = 10

def handle_page(qd):
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

    # Remove duplicates.
    item_links = set()
    items_unique = []
    for item_it in reversed(items):
        item_link = urllib.urlparse(item_it['Link'])
        item_link = item_link._replace(params='', query='', fragment='')
        if item_link in item_links:
            continue
        item_links.add(item_link)
        items_unique.append(item_it)
    items = list(reversed(items_unique))

    #--------------------------------------------------------------------------

    # Body.
    p_it = E.P()
    div_it.append(p_it)
    if surprise > 0:
        p_it.text = "{} out of {} articles. {} pages. Last updated: {}.".format(surprise, len(items), len(dates), timestamp.strftime("%Y-%m-%d %H:%M:%S GMT"))

    # Classifier.
    if len(clfs) != 0:
        scores = np.zeros(len(items))
        langs = set([e['Language'] for e in items])

        for lang_it in langs:
            try:
                clf_it = clfs[lang_it]
            except KeyError:
                continue

            idx = [i for i in range(len(items)) if items[i]['Language'] == lang_it]
            new_titles = [build_feature(items[i]) for i in idx]
            predicted_proba = clf_it.predict_proba(new_titles)
            scores[idx] = [it[1] - it[0] for it in predicted_proba]

        for item_ct in range(len(items)):
            items[item_ct] = dict(items[item_ct])
            items[item_ct]['Score'] = scores[item_ct]
            c.execute("INSERT OR IGNORE INTO {} (UserID, ItemID, Score) VALUES (?, ?, ?)".format(clf), (user_id, items[item_ct]['ItemID'], items[item_ct]['Score'], ))
        conn.commit()

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

# Scrape feeds.
def steins_read(title_pattern=""):
    conn = get_connection()
    c = conn.cursor()

    for feed_it in c.execute("SELECT * FROM Feeds WHERE Title LIKE ?", ("%" + title_pattern + "%", )).fetchall():
        handler = get_handler(feed_it['FeedID'])
        d = handler.parse(feed_it['Link'])
        try:
            logger.info("{} -- {}.".format(feed_it['Title'], d.status))
        except AttributeError:
            logger.info("{}.".format(feed_it['Title']))

        for item_it in d['items']:
            try:
                item_title = handler.read_title(item_it)
                item_link = handler.read_link(item_it)
                item_time = handler.read_time(item_it)
                item_summary = handler.read_summary(item_it)
            except KeyError:
                continue

            add_item(item_title, item_link, item_time, feed_it['FeedID'], item_summary)

        c.execute("UPDATE Feeds SET Updated=(SELECT datetime('now')) WHERE FeedID=?", (feed_it['FeedID'], ))
        conn.commit()

# Generate HTML.
def steins_write():
    c = get_cursor()

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items ORDER BY Published DESC").fetchall()
    for d_ctr in range(len(dates)):
        with open(dir_path+os.sep+"steins-{}.html".format(d_ctr), 'w') as f:
            f.write(handle_page(page=d_ctr))

def steins_update(title_pattern="", read_mode=True, write_mode=False):
    logger.info("Update feeds.")

    if read_mode:
        steins_read(title_pattern)
    if write_mode:
        steins_write()
