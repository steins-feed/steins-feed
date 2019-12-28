#!/usr/bin/env python3

from datetime import datetime
from lxml import etree
import os
import sqlite3
from sqlite3 import IntegrityError, OperationalError
import time

from steins_log import get_logger

dir_path = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "steins.db"
db_path = dir_path + os.sep + DB_NAME
FILE_NAME = "feeds.xml"
file_path = dir_path + os.sep + FILE_NAME

logger = get_logger()

def last_update(record=None):
    conn = get_connection()
    c = conn.cursor()
    if record == None:
        record = datetime.utcnow()
    c.execute("INSERT INTO Updates(Record) VALUES (?)", (record, ))
    conn.commit()
    logger.info("Last update: {}.".format(record))

def last_updated():
    c = get_cursor()
    record = c.execute("SELECT Record FROM Updates ORDER BY ItemID DESC LIMIT 3").fetchone()
    return record[0]

def have_connection():
    if "connection" in globals():
        return True
    else:
        return False

def get_connection():
    global connection
    if not have_connection():
        connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        connection.row_factory = sqlite3.Row
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

def add_feed(title, link, lang, disp=1, summary=2, user='nobody'):
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO Feeds (Title, Link, Language, Summary) VALUES (?, ?, ?, ?)", (title, link, lang, summary, ))
        c.execute("INSERT INTO Display (ItemID) SELECT ItemID FROM Feeds WHERE Title=? AND Link=? AND Language=? AND Summary=?", (title, link, lang, summary, ))
        c.execute("UPDATE Display SET {}=? WHERE ItemID IN (SELECT DISTINCT ItemID FROM Feeds WHERE Title=? AND Link=? AND Language=? AND Summary=?)".format(user), (disp, title, link, lang, summary, ))
        conn.commit()
        logger.info("Add feed -- {}.".format(title))
    except IntegrityError:
        conn.rollback()
        logger.error("Add feed -- {}.".format(title))

def delete_feed(item_id):
    conn = get_connection()
    c = conn.cursor()

    title = c.execute("Select Title FROM Feeds WHERE ItemID=?", (item_id, )).fetchone()[0]
    c.execute("DELETE FROM Feeds WHERE ItemID=?", (item_id, ))
    c.execute("DELETE FROM Display WHERE ItemID=?", (item_id, ))
    logger.info("Delete feed -- {}.".format(title))

    conn.commit()

def init_feeds(file_path=file_path, user='nobody'):
    with open(file_path, 'r') as f:
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
            lang = 'English'
        try:
            summary = feed_it.xpath("./summary")[0].text
        except IndexError:
            summary = 2
        add_feed(title, link, lang, disp, summary, user)

def add_item(item_title, item_time, item_summary, item_source, item_link):
    conn = get_connection()
    c = conn.cursor()

    # Punish cheaters.
    if time.strptime(item_time, "%Y-%m-%d %H:%M:%S GMT") > time.gmtime():
        return

    try:
        c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_title, item_time, item_summary, item_source, item_link, ))
        c.execute("INSERT INTO Like (ItemID) SELECT ItemID FROM Items WHERE Title=? AND Published=? AND Summary=? AND Source=? AND Link=?", (item_title, item_time, item_summary, item_source, item_link, ))
        conn.commit()
        logger.info("Add item -- {}.".format(item_title))
    except IntegrityError:
        conn.rollback()
        logger.error("Add item -- {}.".format(item_title))

def delete_item(item_id):
    conn = get_connection()
    c = conn.cursor()

    title = c.execute("Select Title FROM Items WHERE ItemID=?", (item_id, )).fetchone()[0]
    c.execute("DELETE FROM Items WHERE ItemID=?", (item_id, ))
    c.execute("DELETE FROM Like WHERE ItemID=?", (item_id, ))
    logger.info("Delete item -- {}.".format(title))

    conn.commit()

def add_user(name):
    conn = get_connection()
    c = conn.cursor()

    c.execute("INSERT INTO Users (Name) VALUES (?)", (name, ))
    c.execute("ALTER TABLE Display ADD COLUMN {} INTEGER DEFAULT 0".format(name))
    c.execute("UPDATE Display SET {}=1".format(name))
    c.execute("ALTER TABLE Like ADD COLUMN {} INTEGER DEFAULT 0".format(name))
    logger.warning("Add user -- {}.".format(name))

    conn.commit()

def rename_user(old_name, new_name):
    conn = get_connection()
    c = conn.cursor()

    c.execute("UPDATE Users SET Name=? WHERE Name=?", (new_name, old_name, ))

    name_list = [e[1] for e in c.execute("PRAGMA table_info(Display)").fetchall()]
    name_list.remove(old_name)
    c.execute("ALTER TABLE Display RENAME TO Display_old")
    c.execute("CREATE TABLE Display AS SELECT {} FROM Display_old".format(", ".join(name_list)))
    c.execute("ALTER TABLE Display ADD COLUMN {} INTERGER DEFAULT 0".format(new_name))
    c.execute("UPDATE Display SET {}=(SELECT {} FROM Display_old WHERE ItemID=Display.ItemID)".format(new_name, old_name))
    c.execute("DROP TABLE Display_old")

    name_list = [e[1] for e in c.execute("PRAGMA table_info(Like)").fetchall()]
    name_list.remove(old_name)
    c.execute("ALTER TABLE Like RENAME TO Like_old")
    c.execute("CREATE TABLE Like AS SELECT {} FROM Like_old".format(", ".join(name_list)))
    c.execute("ALTER TABLE Like ADD COLUMN {} INTERGER DEFAULT 0".format(new_name))
    c.execute("UPDATE Like SET {}=(SELECT {} FROM Like_old WHERE ItemID=Like.ItemID)".format(new_name, old_name))
    c.execute("DROP TABLE Like_old")

    logger.warning("Rename user -- {} to {}.".format(old_name, new_name))
    conn.commit()

def delete_user(name):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM Users WHERE Name=?", (name, ))

    name_list = [e[1] for e in c.execute("PRAGMA table_info(Display)").fetchall()]
    name_list.remove(name)
    c.execute("ALTER TABLE Display RENAME TO Display_old")
    c.execute("CREATE TABLE Display AS SELECT {} FROM Display_old".format(", ".join(name_list)))
    c.execute("DROP TABLE Display_old")

    name_list = [e[1] for e in c.execute("PRAGMA table_info(Like)").fetchall()]
    name_list.remove(name)
    c.execute("ALTER TABLE Like RENAME TO Like_old")
    c.execute("CREATE TABLE Like AS SELECT {} FROM Like_old".format(", ".join(name_list)))
    c.execute("DROP TABLE Like_old")

    logger.warning("Delete user -- {}.".format(name))
    conn.commit()

if __name__ == "__main__":
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Feeds (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL UNIQUE, Link TEXT NOT NULL, Language TEXT DEFAULT '', Summary INTEGER DEFAULT 2)")
        c.execute("CREATE TABLE Display (ItemID INTEGER PRIMARY KEY, nobody INTEGER DEFAULT 1)")
        conn.commit()
        logger.warning("Create Feeds.")
    except OperationalError:
        pass

    try:
        c.execute("CREATE TABLE Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL)")
        c.execute("CREATE TABLE Like (ItemID INTEGER PRIMARY KEY, nobody INTEGER DEFAULT 0)")
        conn.commit()
        logger.warning("Create Items.")
    except OperationalError:
        pass

    try:
        c.execute("CREATE TABLE Users (ItemID INTEGER PRIMARY KEY, Name TINYTEXT NOT NULL UNIQUE)")
        c.execute("INSERT INTO Users (Name) VALUES (?)", ("nobody", ))
        conn.commit()
        logger.warning("Create Users.")
    except OperationalError:
        pass

    try:
        c.execute("CREATE TABLE Updates (ItemID INTEGER PRIMARY KEY, Record TIMESTAMP NOT NULL)")
        conn.commit()
        logger.warning("Create Updates.")
    except OperationalError:
        pass

    init_feeds()
    close_connection()
