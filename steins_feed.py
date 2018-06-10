#!/usr/bin/env python3

import feedparser
import os
import requests
import sqlite3
import time

from lxml import etree, html
from steins_manager import SteinsFactory

def add_feed(c, title, link):
    c.execute("INSERT INTO Feeds (Title, Link) VALUES (?, ?)", (title, link, ))

def delete_feed(c, title):
    c.execute("DELETE FROM Feeds WHERE Title='?'", (title, ))

def init_feeds(c):
    f = open("steins_config.xml", 'r')
    tree = etree.fromstring(f.read())
    f.close()

    feed_list = tree.xpath("//feed")
    for feed_it in feed_list:
        title = feed_it.xpath("./title")[0].text
        link = feed_it.xpath("./link")[0].text
        add_feed(c, title, link)

# Scrape feeds.
def steins_read(c):
    factory = SteinsFactory()

    for feed_it in c.execute("SELECT * FROM Feeds").fetchall():
        print(feed_it[1])
        handler = factory.get_handler(feed_it[1])

        d = feedparser.parse(feed_it[2])
        for item_it in d['items']:
            item_title = handler.read_title(item_it)
            item_time = handler.read_time(item_it)
            item_link = handler.read_link(item_it)
            item_summary = handler.read_summary(item_it)

            if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_title, item_time, )).fetchone()[0] == 0:
                c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_title, item_time, item_summary, feed_it[1], item_link, ))

# Generate HTML.
def steins_write(c):
    factory = SteinsFactory()

    dir_name = os.path.dirname(os.path.abspath(__file__))
    times = c.execute("SELECT Published FROM Items")
    times = [t_it[0][:10] for t_it in times]
    dates = sorted(list(set(times)), reverse=True)
    f_list = []

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
        f.write("<h1>{}</h1>\n".format(time.strftime("%A, %d %B %Y", time.strptime(d_it, "%Y-%m-%d"))))
        f.write("<p>{} articles.</p>\n".format(times.count(d_it)))
        f.write("<form>\n")
        if not d_ctr == 0:
            f.write("<input type=\"submit\" formaction=\"/steins-{}.html\" value=\"Previous\">\n".format(d_ctr-1))
        if not d_ctr == len(dates)-1:
            f.write("<input type=\"submit\" formaction=\"/steins-{}.html\" value=\"Next\">\n".format(d_ctr+1))
        f.write("</form>\n")
        f.write("<hr>\n")

        f_list.append(f)

    for row_it in c.execute("SELECT * FROM Items ORDER BY Published DESC"):
        f_idx = dates.index(row_it[2][:10])
        f = f_list[f_idx]

        f.write("<h2><a href=\"{}\">{}</a></h2>\n".format(row_it[5], row_it[1]))
        f.write("<p>Source: {}. Published: {}</p>".format(row_it[4], row_it[2]))
        f.write("{}".format(row_it[3]))

        f.write("<p>\n")
        f.write("<form>\n")
        f.write("<input type=\"submit\" formmethod=\"post\" formaction=\"/like/{}\" value=\"Like\">\n".format(row_it[0]))
        f.write("<input type=\"submit\" formmethod=\"post\" formaction=\"/dislike/{}\" value=\"Dislike\">\n".format(row_it[0]))
        if factory.get_handler(row_it[4]).can_print():
            f.write("<input type=\"submit\" formmethod=\"post\" formaction=\"/print/{}\" value=\"Print\">\n".format(row_it[0]))
        f.write("</form>\n")
        f.write("</p>\n")

        f.write("<hr>\n")

    for d_ctr in range(len(dates)):
        d_it = dates[d_ctr]
        f = f_list[d_ctr]

        f.write("<form>\n")
        if not d_ctr == 0:
            f.write("<input type=\"submit\" formaction=\"/steins-{}.html\" value=\"Previous\">\n".format(d_ctr-1))
        if not d_ctr == len(dates)-1:
            f.write("<input type=\"submit\" formaction=\"/steins-{}.html\" value=\"Next\">\n".format(d_ctr+1))
        f.write("</form>\n")
        f.write("</body>\n")
        f.write("</html>\n")
        f.close()

def steins_update(db_name):
    db_exists = os.path.isfile(db_name)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    if not db_exists:
        c.execute("CREATE TABLE Feeds (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Link TEXT NOT NULL)")
        c.execute("CREATE TABLE Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, Like INTEGER DEFAULT 0)")
        init_feeds(c)
    steins_read(c)
    steins_write(c)
    conn.commit()
    conn.close()
