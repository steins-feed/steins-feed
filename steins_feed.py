#!/usr/bin/env python3

import os
import time

import numpy as np
import numpy.random as random

from steins_config import init_feeds
from steins_manager import get_handler
from steins_sql import get_connection, get_cursor, last_updated

dir_name = os.path.dirname(os.path.abspath(__file__))

# Scrape feeds.
def steins_read():
    conn = get_connection()
    c = conn.cursor()

    for feed_it in c.execute("SELECT * FROM Feeds WHERE DISPLAY=1").fetchall():
        handler = get_handler(feed_it[1])
        d = handler.parse(feed_it[2])
        try:
            print("{}: {}.".format(feed_it[1], d.status))
        except AttributeError:
            print("{}: 200.".format(feed_it[1]))

        for item_it in d['items']:
            try:
                item_title = handler.read_title(item_it)
                item_time = handler.read_time(item_it)
                item_summary = handler.read_summary(item_it)
                item_link = handler.read_link(item_it)
            except KeyError:
                continue

            # Punish cheaters.
            if time.strptime(item_time, "%Y-%m-%d %H:%M:%S GMT") > time.gmtime():
                continue

            # Remove duplicates.
            cands = c.execute("SELECT * FROM Items WHERE Title=?", (item_title, )).fetchall()
            item_exists = False
            for cand_it in cands:
                if not item_time[:10] == cand_it[2][:10]:
                    continue

                idx0_item = item_link.find("//")
                idx1_item = item_link.find("/", idx0_item + 2)
                idx0_cand = cand_it[5].find("//")
                idx1_cand = cand_it[5].find("/", idx0_cand + 2)

                if item_link[:idx1_item] == cand_it[5][:idx1_cand]:
                    item_exists = True
                    break
            if not item_exists:
                c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_title, item_time, item_summary, feed_it[1], item_link, ))
                conn.commit()

def steins_generate_page(page_no, score_board=None, surprise=-1):
    c = get_cursor()

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) ORDER BY Published DESC").fetchall()
    if page_no >= len(dates):
        return
    d_it = dates[page_no][0]
    items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC", (d_it, )).fetchall()

    s = ""
    s += "<!DOCTYPE html>\n"
    s += "<html>\n"
    s += "<head>\n"
    s += "<meta charset=\"UTF-8\">"
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

    s += "<h1>{}</h1>\n".format(time.strftime("%A, %d %B %Y", time.strptime(d_it, "%Y-%m-%d")))
    if surprise > 0:
        s += "<p>{} out of {} articles. {} pages. Last updated: {}.</p>\n".format(surprise, len(items), len(dates), time.strftime("%Y-%m-%d %H:%M:%S GMT", last_updated()))
    else:
        s += "<p>{} articles. {} pages. Last updated: {}.</p>\n".format(len(items), len(dates), time.strftime("%Y-%m-%d %H:%M:%S GMT", last_updated()))

    s += "<p>\n"
    if not page_no == 0:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no-1)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Previous\">\n"
        s += "</form>\n"
    if not page_no == len(dates)-1:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no+1)
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
            s += "<input id=\"like_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" value=\"Like\" style=\"background-color: green\" onclick=\"set_color_like({0})\">\n".format(item_it[0])
        else:
            s += "<input id=\"like_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like.php\" value=\"Like\" onclick=\"set_color_like({0})\">\n".format(item_it[0])
        if item_it[6] == -1:
            s += "<input id=\"dislike_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/dislike.php\" value=\"Dislike\" style=\"background-color: red\" onclick=\"set_color_dislike({0})\">\n".format(item_it[0])
        else:
            s += "<input id=\"dislike_{0}\" type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/dislike.php\" value=\"Dislike\" onclick=\"set_color_dislike({0})\">\n".format(item_it[0])
        s += "</form>\n"
        s += "</p>\n"
        s += "<hr>\n"

    s += "<p>\n"
    if not page_no == 0:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no-1)
        s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/index.php\" value=\"Previous\">\n"
        s += "</form>\n"
    if not page_no == len(dates)-1:
        s += "<form style=\"display: inline-block\">\n"
        s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no+1)
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
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/naive_bayes.php\" value=\"Magic\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/naive_bayes_surprise.php\" value=\"Surprise\">\n"
    s += "</form>\n"
    s += "</p>\n"

    s += "<p>Logistic regression:\n"
    s += "<form style=\"display: inline-block\">\n"
    s += "<input type=\"hidden\" name=\"page\" value=\"{}\">\n".format(page_no)
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/logistic_regression.php\" value=\"Magic\">\n"
    s += "<input type=\"submit\" formmethod=\"get\" formaction=\"/steins-feed/logistic_regression_surprise.php\" value=\"Surprise\">\n"
    s += "</form>\n"
    s += "</p>\n"

    s += "<iframe name=\"foo\" style=\"display: none;\"></iframe>\n"
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

def steins_update(read_mode=True, write_mode=False):
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Feeds (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Link TEXT NOT NULL, Display INTEGER DEFAULT 1)")
    c.execute("CREATE TABLE IF NOT EXISTS Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, Like INTEGER DEFAULT 0)")
    init_feeds()

    conn.commit()

    if read_mode:
        steins_read()
    if write_mode:
        steins_write()

if __name__ == "__main__":
    from steins_sql import close_connection
    from steins_web import close_browser

    steins_update()
    close_connection()
    close_browser()
