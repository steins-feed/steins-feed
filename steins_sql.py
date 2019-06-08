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

def add_feed(title, link, disp=1, lang='', summary=2):
    conn = get_connection()
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO Feeds (Title, Link, Display, Language, Summary) VALUES (?, ?, ?, ?, ?)", (title, link, disp, lang, summary))
    logger.info("Add feed -- {}.".format(title))

    conn.commit()

def delete_feed(item_id):
    conn = get_connection()
    c = conn.cursor()

    title = c.execute("Select Title FROM Feeds WHERE ItemID=?", (item_id, )).fetchone()[0]
    c.execute("DELETE FROM Feeds WHERE ItemID=?", (item_id, ))
    logger.info("Delete feed -- {}.".format(title))

    conn.commit()

def init_feeds(file_path=file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        tree = etree.fromstring(f.read())

    logger.warning("Initialize feeds -- {}.".format(file_path))
    feed_list = tree.xpath("//feed")
    for feed_it in feed_list:
        title = feed_it.xpath("./title")[0].text
        link = feed_it.xpath("./link")[0].text
        try:
            disp = feed_it.xpath("./disp")[0].text
        except IndexError:
            disp = 1
        try:
            lang = feed_it.xpath("./lang")[0].text
        except IndexError:
            lang = ''
        try:
            summary = feed_it.xpath("./summary")[0].text
        except IndexError:
            summary = 2
        add_feed(title, link, disp, lang, summary)

def add_item(item_title, item_time, item_summary, item_source, item_link):
    conn = get_connection()
    c = conn.cursor()
    logger = get_logger()

    # Punish cheaters.
    if time.strptime(item_time, "%Y-%m-%d %H:%M:%S GMT") > time.gmtime():
        return

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
        c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_title, item_time, item_summary, item_source, item_link, ))
        logger.info("Add item -- {}.".format(item_title))
        conn.commit()

def delete_item(item_id):
    conn = get_connection()
    c = conn.cursor()

    title = c.execute("Select Title FROM Items WHERE ItemID=?", (item_id, )).fetchone()[0]
    c.execute("DELETE FROM Items WHERE ItemID=?", (item_id, ))
    logger.info("Delete item -- {}.".format(title))

    conn.commit()

if __name__ == "__main__":
    conn = get_connection()
    c = conn.cursor()
    logger = get_logger()

    c.execute("CREATE TABLE IF NOT EXISTS Feeds (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL UNIQUE, Link TEXT NOT NULL, Display INTEGER DEFAULT 1, Language TEXT DEFAULT '', Summary INTEGER DEFAULT 2)")
    logger.warning("Create Feeds.")
    c.execute("CREATE TABLE IF NOT EXISTS Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, Like INTEGER DEFAULT 0)")
    logger.warning("Create Items.")
    conn.commit()

    init_feeds()
    close_connection()
