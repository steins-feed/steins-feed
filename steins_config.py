#!/usr/bin/env python3

import os

from lxml import etree

def add_feed(c, title, link):
    if c.execute("SELECT COUNT(*) FROM Feeds WHERE Title=?", (title, )).fetchone()[0] == 0:
        c.execute("INSERT INTO Feeds (Title, Link) VALUES (?, ?)", (title, link, ))
        print("ADD: {} <{}>.".format(title, link))

def delete_feed(c, title):
    row = c.execute("SELECT * FROM Feeds WHERE Title=?", (title, )).fetchone()
    c.execute("DELETE FROM Feeds WHERE Title=?", (title, ))
    print("DELETE: {} <{}>.".format(row[1], row[2]))

def init_feeds(c, filename="feeds.xml"):
    dir_name = os.path.dirname(os.path.abspath(__file__))
    f = open(dir_name+os.sep+filename, 'r')
    tree = etree.fromstring(f.read())
    f.close()

    feed_list = tree.xpath("//feed")
    for feed_it in feed_list:
        title = feed_it.xpath("./title")[0].text
        link = feed_it.xpath("./link")[0].text
        add_feed(c, title, link)
