#!/usr/bin/env python3

import os
import sqlite3
import sys
import time

from steins_config import init_feeds
from steins_manager import get_handler

# Scrape feeds.
def steins_read(db_name):
    conn = sqlite3.connect(db_name)
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
    conn.close()

# Generate HTML.
def steins_write_payload(db_name, page_no):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1) ORDER BY Published DESC").fetchall()
    times = [it[2][:10] for it in items]
    dates = sorted(list(set(times)), reverse=True)
    try:
        d_it = dates[page_no]
    except IndexError:
        return

    s = ""

    s += "<h1>{}</h1>\n".format(time.strftime("%A, %d %B %Y", time.strptime(d_it, "%Y-%m-%d")))
    last_updated = time.gmtime(os.path.getmtime(db_name))
    s += "<p>{} articles. {} pages. Last updated: {}.</p>\n".format(times.count(d_it), len(dates), time.strftime("%Y-%m-%d %H:%M:%S GMT", last_updated))
    s += "<form>\n"
    if not page_no == 0:
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/index.php?page={}\" value=\"Previous\">\n".format(page_no-1)
    if not page_no == len(dates)-1:
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/index.php?page={}\" value=\"Next\">\n".format(page_no+1)
    s += "</form>\n"
    s += "<hr>\n"

    for item_it in items:
        if not d_it == item_it[2][:10]:
            continue

        s += "<h2><a href=\"{}\">{}</a></h2>\n".format(item_it[5], item_it[1])
        s += "<p>Source: {}. Published: {}.</p>".format(item_it[4], item_it[2])
        s += "{}".format(item_it[3])

        s += "<p>\n"
        s += "<form>\n"
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/like/{}\" value=\"Like\">\n".format(item_it[0])
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/dislike/{}\" value=\"Dislike\">\n".format(item_it[0])
        s += "</form>\n"
        s += "</p>\n"
        s += "<hr>\n"

    s += "<form>\n"
    if not page_no == 0:
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/index.php?page={}\" value=\"Previous\">\n".format(page_no-1)
    if not page_no == len(dates)-1:
        s += "<input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/index.php?page={}\" value=\"Next\">\n".format(page_no+1)
    s += "</form>\n"

    s += "<p><a href=\"/settings\">Settings</a></p>\n"

    conn.close()

    return s

def steins_write(db_name):
    dir_name = os.path.dirname(os.path.abspath(__file__))
    items = c.execute("SELECT * FROM Items WHERE Source IN (SELECT Title FROM Feeds WHERE Display=1)").fetchall()
    times = [it[2][:10] for it in items]
    dates = sorted(list(set(times)), reverse=True)

    for d_ctr in range(len(dates)):
        d_it = dates[d_ctr]
        f = open(dir_name+os.sep+"steins-{}.html".format(d_ctr), 'w')

        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n")
        f.write("<head>\n")
        f.write("<meta charset=\"UTF-8\">")
        f.write("<title>Stein's Feed</title>\n")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write(steins_write_payload(db_name, d_ctr))
        f.write("</body>\n")
        f.write("</html>\n")
        f.close()

def steins_update(db_name):
    db_exists = os.path.isfile(db_name)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    if not db_exists:
        c.execute("CREATE TABLE Feeds (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Link TEXT NOT NULL, Display INTEGER DEFAULT 1)")
        c.execute("CREATE TABLE Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, Like INTEGER DEFAULT 0)")
        init_feeds(c)
    conn.commit()
    conn.close()

    if not "--no-read" in sys.argv:
        steins_read(db_name)
    if not "--no-write" in sys.argv:
        steins_write(db_name)
