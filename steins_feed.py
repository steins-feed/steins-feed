#!/usr/bin/env python3

import os
import time
from xml.sax.saxutils import unescape

import numpy as np
import numpy.random as random

from steins_log import get_logger
from steins_magic import build_feature
from steins_manager import get_handler
from steins_sql import add_item, get_cursor, last_updated

dir_name = os.path.dirname(os.path.abspath(__file__))

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

def steins_generate_page(page_no="0", lang="International", user="nobody", scorer=[], surprise=-1):
    c = get_cursor()
    page_no = int(page_no)

    if lang == "International":
        dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM (SELECT Feeds.*, Display.{0} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID) WHERE {0}=1) ORDER BY Published DESC".format(user)).fetchall()
    else:
        dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM (SELECT Feeds.*, Display.{0} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID) WHERE {0}=1 AND Language=?) ORDER BY Published DESC".format(user), (lang, )).fetchall()
    if page_no >= len(dates):
        return
    d_it = dates[page_no][0]
    if lang == "International":
        items = c.execute("SELECT Items.*, Like.{0}, Feeds.Language FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE Source IN (SELECT Title FROM (SELECT Feeds.*, Display.{0} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID) WHERE {0}=1) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC".format(user), (d_it, )).fetchall()
    else:
        items = c.execute("SELECT Items.*, Like.{0}, Feeds.Language FROM (Items INNER JOIN Like ON Items.ItemID=Like.ItemID) INNER JOIN Feeds ON Items.Source=Feeds.Title WHERE Source IN (SELECT Title FROM (SELECT Feeds.*, Display.{0} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID) WHERE {0}=1 AND Language=?) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC".format(user), (lang, d_it)).fetchall()

    s = ""
    s += "<!DOCTYPE html>\n"
    s += "<html>\n"
    s += "<head>\n"
    s += "<meta charset=\"UTF-8\">\n"
    s += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>\n"
    s += "<title>Stein's Feed</title>\n"
    s += "<script>\n"
    s += "function set_color_like(button_id) {\n"
    s += "    var stat_like = document.getElementById('like_' + button_id);\n"
    s += "    var stat_dislike = document.getElementById('dislike_' + button_id);\n"
    s += "    if (stat_like.style.backgroundColor == 'green') {\n"
    s += "        stat_like.style.backgroundColor = '';\n"
    s += "    } else {\n"
    s += "        stat_like.style.backgroundColor = 'green';\n"
    s += "    }\n"
    s += "    stat_dislike.style.backgroundColor = '';\n"
    s += "}\n"
    s += "</script>\n"
    s += "<script>\n"
    s += "function set_color_dislike(button_id) {\n"
    s += "    var stat_like = document.getElementById('like_' + button_id);\n"
    s += "    var stat_dislike = document.getElementById('dislike_' + button_id);\n"
    s += "    if (stat_dislike.style.backgroundColor == 'red') {\n"
    s += "        stat_dislike.style.backgroundColor = '';\n"
    s += "    } else {\n"
    s += "        stat_dislike.style.backgroundColor = 'red';\n"
    s += "    }\n"
    s += "    stat_like.style.backgroundColor = '';\n"
    s += "}\n"
    s += "</script>\n"
    s += "</head>\n"
    s += "<body>\n"

    langs = c.execute("SELECT DISTINCT Language FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE {}=1".format(user)).fetchall()
    s += "<p align=right>\n"
    s += "<span style=\"float: left;\">[<a id=top href=#bottom>Bottom</a>]</span>\n"
    s += "<a href=\"/steins-feed/index.php?user={}\">International</a>\n".format(user)
    for lang_it in langs:
        s += "<a href=\"/steins-feed/index.php?lang={0}&user={1}\">{0}</a>\n".format(lang_it[0], user)
    s += "</p>\n"

    s += "<h1>{}</h1>\n".format(time.strftime("%A, %d %B %Y", time.strptime(d_it, "%Y-%m-%d")))
    if surprise > 0:
        s += "<p>{} out of {} articles. {} pages. Last updated: {}.</p>\n".format(surprise, len(items), len(dates), time.strftime("%Y-%m-%d %H:%M:%S GMT", last_updated()))
    else:
        s += "<p>{} articles. {} pages. Last updated: {}.</p>\n".format(len(items), len(dates), time.strftime("%Y-%m-%d %H:%M:%S GMT", last_updated()))

    s += "<p>\n"
    if not page_no == 0:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no-1)
        s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
        s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Previous\">\n"
        s += "</form>\n"
    if not page_no == len(dates)-1:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no+1)
        s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
        s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Next\">\n"
        s += "</form>\n"
    s += "</p>\n"
    s += "<hr>\n"

    if len(scorer) != 0:
        scores = np.zeros(len(items))
        langs = set([e['Language'] for e in items])

        for lang_it in langs:
            try:
                clf = scorer[lang_it]
            except KeyError:
                continue

            idx = [i for i in range(len(items)) if items[i]['Language'] == lang_it]
            new_titles = [build_feature(items[i]) for i in idx]
            predicted_proba = clf.predict_proba(new_titles)
            scores[idx] = [it[1] - it[0] for it in predicted_proba]

        for item_ct in range(len(items)):
            items[item_ct] = dict(items[item_ct])
            items[item_ct]['Score'] = scores[item_ct]

    if surprise > 0:
        logit_scores = np.log((1. + scores) / (1. - scores))
        sigma = np.sqrt(np.sum(logit_scores**2) / scores.size)
        probs = np.exp(-0.5 * logit_scores**2 / sigma**2) / (1. + scores) / (1. - scores) / sigma / np.sqrt(2. * np.pi)
        probs /= np.sum(probs)
        sample = random.choice(scores.size, surprise, False, probs)
        items = [items[cnt] for cnt in sample]
    elif len(scorer) != 0:
        items = sorted(items, key=lambda item_it: item_it['Score'], reverse=True)

    for item_it in items:
        s += "<h2><a target=\"_blank\" rel=\"noopener noreferrer\" href=\"{}\">{}</a></h2>\n".format(unescape(item_it['Link']), unescape(item_it['Title']))
        if len(scorer) != 0:
            s += "<p>Source: {}. Published: {}. Score: {:.2f}.</p>\n".format(unescape(item_it['Source']), item_it['Published'], item_it['Score'])
        else:
            s += "<p>Source: {}. Published: {}.</p>\n".format(unescape(item_it['Source']), item_it['Published'])
        s += "{}".format(unescape(item_it['Summary']))

        s += "<p>\n"
        s += "<form target=\"foo\">\n"
        s += "<input type=\"hidden\" name=\"id\" value=\"{}\">\n".format(item_it['ItemID'])
        s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
        if item_it['{}'.format(user)] == 1:
            s += "<input id=\"like_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" name=\"submit\" value=\"Like\" style=\"background-color: green\" onclick=\"set_color_like({0})\">\n".format(item_it['ItemID'])
        else:
            s += "<input id=\"like_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" name=\"submit\" value=\"Like\" onclick=\"set_color_like({0})\">\n".format(item_it['ItemID'])
        if item_it['{}'.format(user)] == -1:
            s += "<input id=\"dislike_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" name=\"submit\" value=\"Dislike\" style=\"background-color: red\" onclick=\"set_color_dislike({0})\">\n".format(item_it['ItemID'])
        else:
            s += "<input id=\"dislike_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" name=\"submit\" value=\"Dislike\" onclick=\"set_color_dislike({0})\">\n".format(item_it['ItemID'])
        s += "</form>\n"
        s += "</p>\n"
        s += "<hr>\n"

    s += "<p>\n"
    if not page_no == 0:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no-1)
        s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
        s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Previous\">\n"
        s += "</form>\n"
    if not page_no == len(dates)-1:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no+1)
        s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
        s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Next\">\n"
        s += "</form>\n"
    s += "</p>\n"

    s += "<p>\n"
    s += "<a href=\"/steins-feed/settings.php?user={}\">Settings</a>\n".format(user)
    s += "<a href=\"/steins-feed/statistics.php?user={}\">Statistics</a>\n".format(user)
    s += "</p>\n"
    s += "<hr>\n"

    s += "<p>Naive Bayes:\n"
    s += "<form style=\"display: inline-block\">\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
    s += "<input type=\"hidden\" name=\"classifier\" value=\"Naive Bayes\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/magic.php\" name=\"submit\" value=\"Magic\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/magic.php\" name=\"submit\" value=\"Surprise\">\n"
    s += "</form>\n"
    s += "</p>\n"

    s += "<p>Logistic regression:\n"
    s += "<form style=\"display: inline-block\">\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(user)
    s += "<input type=\"hidden\" name=\"classifier\" value=\"Logistic Regression\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/magic.php\" name=\"submit\" value=\"Magic\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/magic.php\" name=\"submit\" value=\"Surprise\">\n"
    s += "</form>\n"
    s += "</p>\n"

    s += "<iframe name=\"foo\" style=\"display: none;\"></iframe>\n"
    s += "<p align=right>\n"
    s += "<span style=\"float: left;\">[<a id=bottom href=#top>Top</a>]</span>\n"
    s += "</p>\n"
    s += "</body>\n"
    s += "</html>\n"

    return s

# Generate HTML.
def steins_write():
    c = get_cursor()

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items ORDER BY Published DESC").fetchall()
    for d_ctr in range(len(dates)):
        with open(dir_name+os.sep+"steins-{}.html".format(d_ctr), 'w') as f:
            f.write(steins_generate_page(d_ctr))

def steins_update(title_pattern="", read_mode=True, write_mode=False):
    if read_mode:
        steins_read(title_pattern)
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
