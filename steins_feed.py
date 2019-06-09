#!/usr/bin/env python3

import os
import time

import numpy as np
import numpy.random as random

from steins_log import get_logger
from steins_manager import get_handler
from steins_sql import add_item, get_cursor, last_updated

dir_name = os.path.dirname(os.path.abspath(__file__))

# Scrape feeds.
def steins_read(title_pattern=""):
    c = get_cursor()
    logger = get_logger()

    for feed_it in c.execute("SELECT * FROM Feeds WHERE Title LIKE ? AND DISPLAY=1", ("%" + title_pattern + "%", )).fetchall():
        handler = get_handler(feed_it[1])
        d = handler.parse(feed_it[2])
        try:
            logger.info("{} -- {}.".format(feed_it[1], d.status))
        except AttributeError:
            logger.info("{}.".format(feed_it[1]))

        for item_it in d['items']:
            try:
                item_title = handler.read_title(item_it)
                item_time = handler.read_time(item_it)
                item_summary = handler.read_summary(item_it)
                item_link = handler.read_link(item_it)
            except KeyError:
                continue

            add_item(item_title, item_time, item_summary, feed_it[1], item_link)

def steins_generate_page(page_no=0, lang="International", score_board=None, surprise=-1):
    c = get_cursor()

    if lang == "International":
        dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) ORDER BY Published DESC").fetchall()
    else:
        dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1 AND Language=?) ORDER BY Published DESC", (lang, )).fetchall()
    if page_no >= len(dates):
        return
    d_it = dates[page_no][0]
    if lang == "International":
        items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC", (d_it, )).fetchall()
    else:
        items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1 AND Language=?) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC", (lang, d_it)).fetchall()

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

    langs = c.execute("SELECT DISTINCT Language FROM Feeds").fetchall()
    s += "<p align=right>\n"
    s += "<span style=\"float: left;\">[<a id=top href=#bottom>Bottom</a>]</span>\n"
    s += "<a href=\"/steins-feed/index.php\">International</a>\n"
    for lang_it in langs:
        s += "<a href=\"/steins-feed/index.php?lang={0}\">{0}</a>\n".format(lang_it[0])
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
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Previous\">\n"
        s += "</form>\n"
    if not page_no == len(dates)-1:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no+1)
        s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Next\">\n"
        s += "</form>\n"
    s += "</p>\n"
    s += "<hr>\n"

    if surprise > 0:
        scores = np.array([it[0] for it in score_board])
        scores = 0.5 * (1. + scores)
        logit_scores = np.log(scores / (1. - scores))
        sigma = np.sqrt(np.sum(logit_scores**2) / scores.size)
        probs = np.exp(-0.5 * logit_scores**2 / sigma**2) / scores / (1. - scores) / sigma / np.sqrt(2. * np.pi)
        probs /= np.sum(probs)
        sample = random.choice(scores.size, surprise, False, probs)

    for item_ctr in range(len(items)):
        if surprise == 0:
            break
        elif surprise > 0:
            surprise -= 1
            item_it = items[score_board[sample[surprise]][1]]
        elif not score_board is None:
            item_it = items[score_board[item_ctr][1]]
        else:
            item_it = items[item_ctr]

        s += "<h2><a target=\"_blank\" rel=\"noopener noreferrer\" href=\"{}\">{}</a></h2>\n".format(item_it[5], item_it[1])
        if surprise >= 0:
            s += "<p>Source: {}. Published: {}. Score: {:.2f}.</p>\n".format(item_it[4], item_it[2], score_board[sample[surprise]][0])
        elif not score_board is None:
            s += "<p>Source: {}. Published: {}. Score: {:.2f}.</p>\n".format(item_it[4], item_it[2], score_board[item_ctr][0])
        else:
            s += "<p>Source: {}. Published: {}.</p>\n".format(item_it[4], item_it[2])
        s += "{}".format(item_it[3])

        s += "<p>\n"
        s += "<form target=\"foo\">\n"
        s += "<input type=\"hidden\" name=\"id\" value=\"{}\">\n".format(item_it[0])
        if item_it[6] == 1:
            s += "<input id=\"like_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" name=\"submit\" value=\"Like\" style=\"background-color: green\" onclick=\"set_color_like({0})\">\n".format(item_it[0])
        else:
            s += "<input id=\"like_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" name=\"submit\" value=\"Like\" onclick=\"set_color_like({0})\">\n".format(item_it[0])
        if item_it[6] == -1:
            s += "<input id=\"dislike_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" name=\"submit\" value=\"Dislike\" style=\"background-color: red\" onclick=\"set_color_dislike({0})\">\n".format(item_it[0])
        else:
            s += "<input id=\"dislike_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" name=\"submit\" value=\"Dislike\" onclick=\"set_color_dislike({0})\">\n".format(item_it[0])
        s += "</form>\n"
        s += "</p>\n"
        s += "<hr>\n"

    s += "<p>\n"
    if not page_no == 0:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no-1)
        s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Previous\">\n"
        s += "</form>\n"
    if not page_no == len(dates)-1:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no+1)
        s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Next\">\n"
        s += "</form>\n"
    s += "</p>\n"

    s += "<p>\n"
    s += "<a href=\"/steins-feed/settings.php\">Settings</a>\n"
    s += "<a href=\"/steins-feed/statistics.php\">Statistics</a>\n"
    s += "</p>\n"
    s += "<hr>\n"

    s += "<p>Naive Bayes:\n"
    s += "<form style=\"display: inline-block\">\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/naive_bayes.php\" value=\"Magic\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/naive_bayes_surprise.php\" value=\"Surprise\">\n"
    s += "</form>\n"
    s += "</p>\n"

    s += "<p>Logistic regression:\n"
    s += "<form style=\"display: inline-block\">\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"hidden\" name=\"lang\" value=\"{}\">\n".format(lang)
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/logistic_regression.php\" value=\"Magic\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/logistic_regression_surprise.php\" value=\"Surprise\">\n"
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

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) ORDER BY Published DESC").fetchall()
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
