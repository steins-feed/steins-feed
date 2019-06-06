#!/usr/bin/env python3

import os

from lxml import etree

from steins_log import get_logger
from steins_sql import get_connection

FILE_NAME = "feeds.xml"
dir_path = os.path.dirname(os.path.abspath(__file__))
file_path = dir_path + os.sep + FILE_NAME

def add_feed(title, link):
    conn = get_connection()
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO Feeds (Title, Link) VALUES (?, ?)", (title, link, ))
    get_logger().warning("Add feed -- {}.".format(title))

    conn.commit()

def delete_feed(title):
    conn = get_connection()
    c = conn.cursor()

    row = c.execute("SELECT * FROM Feeds WHERE Title=?", (title, )).fetchone()
    c.execute("DELETE FROM Feeds WHERE Title=?", (title, ))
    get_logger().warning("Delete feed -- {}.".format(title))

    conn.commit()

def init_feeds(file_path=file_path):
    with open(file_path, 'r') as f:
        tree = etree.fromstring(f.read())

    get_logger().warning("Initialize feeds -- {}.".format(file_path))
    feed_list = tree.xpath("//feed")
    for feed_it in feed_list:
        title = feed_it.xpath("./title")[0].text
        link = feed_it.xpath("./link")[0].text
        add_feed(title, link)

if __name__ == "__main__":
    from steins_sql import close_connection

    init_feeds()
    close_connection()
