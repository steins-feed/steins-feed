#!/usr/bin/env python3

import feedparser
import os
import requests
import sqlite3
import time

from lxml import html
from steins_manager import init_feeds, can_print

def steins_read_time(item_it):
    try:
        item_time = item_it['published_parsed']
        item_time = time.strftime("%Y-%m-%d %H:%M:%S", item_time)
        return item_time
    except:
        pass

    try:
        item_time = item_it['published']
        item_time = time.strptime(item_time, "%m/%d/%Y %I:%M:%S %p")
        item_time = time.strftime("%Y-%m-%d %H:%M:%S", item_time)
        return item_time
    except:
        pass

    try:
        item_time = item_it['updated_parsed']
        item_time = time.strftime("%Y-%m-%d %H:%M:%S", item_time)
        return item_time
    except:
        pass

    try:
        item_time = item_it['updated']
        item_time = time.strptime(item_time, "%m/%d/%Y %I:%M:%S %p")
        item_time = time.strftime("%Y-%m-%d %H:%M:%S", item_time)
        return item_time
    except:
        pass

    raise KeyError

# Scrape feeds.
def steins_read(c):
    for feed_it in c.execute("SELECT * FROM Feeds").fetchall():
        print(feed_it[1])
        d = feedparser.parse(feed_it[2])

        for item_it in d['items']:
            item_title = item_it['title']
            item_time = steins_read_time(item_it)
            item_link = item_it['link']

            # item_summary.
            if "Atlantic" in feed_it[1]:
                if "/video/" in item_link:
                    continue
                if "/photo/" in item_link:
                    continue

                page = requests.get(item_link)
                tree = html.fromstring(page.content)
                nodes = tree.xpath("//p[@itemprop='description']")
                item_summary = nodes[0].text
            else:
                item_summary = item_it['summary']

            if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_title, item_time, )).fetchone()[0] == 0:
                c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_title, item_time, item_summary, feed_it[1], item_link, ))

# Generate HTML.
def steins_write(c):
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
        if can_print(row_it[4]):
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
