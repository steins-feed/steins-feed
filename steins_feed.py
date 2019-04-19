#!/usr/bin/env python3

import os
import time

from steins_config import init_feeds
from steins_manager import get_handler
from steins_sql import get_connection, get_cursor, last_updated

dir_name = os.path.dirname(os.path.abspath(__file__))

# Scrape feeds.
def steins_read():
    conn = get_connection()
    c = conn.cursor()

    for feed_it in c.execute("SELECT * FROM Feeds WHERE DISPLAY=1").fetchall():
        print(feed_it[1])
        handler = get_handler(feed_it[1])
        d = handler.parse(feed_it[2])

        for item_it in d['items']:
            item_title = handler.read_title(item_it)
            item_time = handler.read_time(item_it)

            # Punish cheaters.
            if time.strptime(item_time, "%Y-%m-%d %H:%M:%S GMT") > time.gmtime():
                continue

            if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_title, item_time, )).fetchone()[0] == 0:
                item_link = handler.read_link(item_it)
                item_summary = handler.read_summary(item_it)
                c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_title, item_time, item_summary, feed_it[1], item_link, ))

    conn.commit()

def steins_write_body(page_no):
    c = get_cursor()

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) ORDER BY Published DESC").fetchall()
    if page_no >= len(dates):
        return
    d_it = dates[page_no][0]
    items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) AND SUBSTR(Published, 1, 10)=? ORDER BY Published DESC", (d_it, )).fetchall()

    s = ""

    s += "<h1>{}</h1>\n".format(time.strftime("%A, %d %B %Y", time.strptime(d_it, "%Y-%m-%d")))
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

    for item_it in items:
        s += "<h2><a href=\"{}\">{}</a></h2>\n".format(item_it[5], item_it[1])
        s += "<p>Source: {}. Published: {}.</p>".format(item_it[4], item_it[2])
        s += "{}".format(item_it[3])

        s += "<p>\n"
        s += "<form>\n"
        s += "<input type=\"hidden\" name=\"id\" value=\"{}\">\n".format(item_it[0])
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/like\" value=\"Like\">\n"
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/dislike\" value=\"Dislike\">\n"
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

    s += "<p><a href=\"/steins-feed/settings.php\">Settings</a></p>\n"

    return s

# Generate HTML.
def steins_write():
    c = get_cursor()

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) ORDER BY Published DESC").fetchall()
    for d_ctr in range(len(dates)):
        with open(dir_name+os.sep+"steins-{}.html".format(d_ctr), 'w') as f:
            f.write("<!DOCTYPE html>\n")
            f.write("<html>\n")
            f.write("<head>\n")
            f.write("<meta charset=\"UTF-8\">")
            f.write("<title>Stein's Feed</title>\n")
            f.write("</head>\n")
            f.write("<body>\n")
            f.write(steins_write_body(d_ctr))
            f.write("</body>\n")
            f.write("</html>\n")

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
    steins_update()
