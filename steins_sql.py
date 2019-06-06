#!/usr/bin/env python3

import os
import sqlite3
import time

from lxml import etree

from steins_log import get_logger

dir_path = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "steins.db"
db_path = dir_path + os.sep + DB_NAME
FILE_NAME = "feeds.xml"
file_path = dir_path + os.sep + FILE_NAME

logger = get_logger()

def last_updated():
    t = os.path.getmtime(db_path)
    t = time.gmtime(t)
    return t

def have_connection():
    if "connection" in globals():
        return True
    else:
        return False

def get_connection():
    global connection
    if not have_connection():
        connection = sqlite3.connect(db_path)
        #connection = sqlite3.connect(db_path, isolation_level=None)
        logger.debug("Open {}.".format(db_path))
    return connection

def close_connection():
    if have_connection():
        conn = get_connection()
        conn.close()
        logger.debug("Close {}.".format(db_path))

def have_cursor():
    if "cursor" in globals():
        return True
    else:
        return False

def get_cursor():
    global cursor
    if not have_cursor():
        conn = get_connection()
        cursor = conn.cursor()
    return cursor

def add_feed(title, link):
    conn = get_connection()
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO Feeds (Title, Link) VALUES (?, ?)", (title, link, ))
    logger.info("Add feed -- {}.".format(title))

    conn.commit()

def delete_feed(title):
    conn = get_connection()
    c = conn.cursor()

    row = c.execute("SELECT * FROM Feeds WHERE Title=?", (title, )).fetchone()
    c.execute("DELETE FROM Feeds WHERE Title=?", (title, ))
    logger.info("Delete feed -- {}.".format(title))

    conn.commit()

def init_feeds(file_path=file_path):
    with open(file_path, 'r') as f:
        tree = etree.fromstring(f.read())

    logger.warning("Initialize feeds -- {}.".format(file_path))
    feed_list = tree.xpath("//feed")
    for feed_it in feed_list:
        title = feed_it.xpath("./title")[0].text
        link = feed_it.xpath("./link")[0].text
        add_feed(title, link)

if __name__ == "__main__":
    conn = get_connection()
    c = conn.cursor()
    logger = get_logger()

    c.execute("CREATE TABLE IF NOT EXISTS Feeds (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL UNIQUE, Link TEXT NOT NULL, Display INTEGER DEFAULT 1)")
    logger.warning("Create Feeds.")
    c.execute("CREATE TABLE IF NOT EXISTS Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, Like INTEGER DEFAULT 0)")
    logger.warning("Create Items.")
    conn.commit()

    init_feeds()
    close_connection()
