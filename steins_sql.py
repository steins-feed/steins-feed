#!/usr/bin/env python3

from datetime import datetime
import os
import sqlite3

dir_path = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "steins.db"
db_path = dir_path + os.sep + DB_NAME

from steins_config import clf_dict
from steins_log import get_logger
logger = get_logger()

###############################################################################
# SQLite connection and cursor.
###############################################################################

def have_connection():
    if 'connection' in globals():
        return True
    else:
        return False

def get_connection():
    global connection
    if not have_connection():
        connection = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        logger.debug("Open {}.".format(db_path))
    return connection

def close_connection():
    if have_connection():
        conn = get_connection()
        conn.close()
        logger.debug("Close {}.".format(db_path))

def have_cursor():
    if 'cursor' in globals():
        return True
    else:
        return False

def get_cursor():
    global cursor
    if not have_cursor():
        conn = get_connection()
        cursor = conn.cursor()
    return cursor

###############################################################################
# Create tables.
###############################################################################

def create_users():
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Users (UserID INTEGER PRIMARY KEY, Name TINYTEXT NOT NULL UNIQUE)")

    conn.commit()
    logger.info("Create Users.")

def create_feeds():
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Feeds (FeedID INTEGER PRIMARY KEY, Title TEXT NOT NULL UNIQUE, Link TEXT NOT NULL UNIQUE, Language TINYTEXT DEFAULT '', Summary INTEGER DEFAULT 2, Added TIMESTAMP DEFAULT CURRENT_TIMESTAMP, Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

    conn.commit()
    logger.info("Create Feeds.")

def create_items():
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Link TEXT NOT NULL, Published TIMESTAMP NOT NULL, FeedID INTEGER NOT NULL, Summary MEDIUMTEXT, FOREIGN KEY (FeedID) REFERENCES Feeds (FeedID) ON UPDATE CASCADE ON DELETE CASCADE, UNIQUE(Title, Link, Published, FeedID))")

    conn.commit()
    logger.info("Create Items.")

def create_display():
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Display (UserID INTEGER NOT NULL, FeedID INTEGER NOT NULL, FOREIGN KEY (UserID) REFERENCES Users (UserID) ON UPDATE CASCADE ON DELETE CASCADE, FOREIGN KEY (FeedID) REFERENCES Feeds (FeedID) ON UPDATE CASCADE ON DELETE CASCADE, UNIQUE(UserID, FeedID))")

    conn.commit()
    logger.info("Create Display.")

def create_like():
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Like (UserID INTEGER NOT NULL, ItemID INTEGER NOT NULL, Score INTEGER NOT NULL, Added TIMESTAMP DEFAULT CURRENT_TIMESTAMP, Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (UserID) REFERENCES Users (UserID) ON UPDATE CASCADE ON DELETE CASCADE, FOREIGN KEY (ItemID) REFERENCES Items (ItemID) ON UPDATE CASCADE ON DELETE CASCADE, UNIQUE(UserID, ItemID))")

    conn.commit()
    logger.info("Create Like.")

def create_magic():
    conn = get_connection()
    c = conn.cursor()

    for clf_it in clf_dict:
        c.execute("CREATE TABLE IF NOT EXISTS {} (UserID INTEGER NOT NULL, ItemID INTEGER NOT NULL, Score FLOAT NOT NULL, Added TIMESTAMP DEFAULT CURRENT_TIMESTAMP, Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (UserID) REFERENCES Users (UserID) ON UPDATE CASCADE ON DELETE CASCADE, FOREIGN KEY (ItemID) REFERENCES Items (ItemID) ON UPDATE CASCADE ON DELETE CASCADE, UNIQUE(UserID, ItemID))".format(clf_it.replace(" ", "")))

    conn.commit()
    logger.info("Create Magic.")

###############################################################################
# Modify tables.
###############################################################################

def add_user(name):
    conn = get_connection()
    c = conn.cursor()

    c.execute("INSERT OR IGNORE INTO Users (Name) VALUES (?)", (name, ))

    conn.commit()
    logger.info("Add user -- {}.".format(name))

def delete_user(user_id):
    conn = get_connection()
    c = conn.cursor()

    for user_it in c.execute("SELECT Name FROM Users WHERE UserID=?", (user_id, )).fetchall():
        c.execute("DELETE FROM Users WHERE UserID=? AND Name=?", (user_id, user_it['Name'], ))
        logger.info("Delete user -- {}.".format(user_it['Name']))

    conn.commit()

def add_feed(title, link, lang='', summary=2):
    c = get_cursor()

    c.execute("INSERT OR IGNORE INTO Feeds (Title, Link, Language, Summary) VALUES (?, ?, ?, ?)", (title, link, lang, summary, ))
    logger.debug("Add feed -- {}.".format(title))

def delete_feed(feed_id):
    conn = get_connection()
    c = conn.cursor()

    for feed_it in c.execute("SELECT Title FROM Feeds WHERE FeedID=?", (feed_id, )).fetchall():
        c.execute("DELETE FROM Feeds WHERE FeedID=? AND Title=?", (feed_id, feed_it['Title'], ))
        logger.info("Delete feed -- {}.".format(feed_it['Title']))

    conn.commit()

def add_item(item_title, item_link, item_time, feed_id, item_summary=""):
    c = get_cursor()

    # Punish cheaters.
    if item_time > datetime.utcnow():
        return

    c.execute("INSERT OR IGNORE INTO Items (Title, Link, Published, FeedID, Summary) VALUES (?, ?, ?, ?, ?)", (item_title, item_link, item_time, feed_id, item_summary, ))
    logger.debug("Add item -- {}.".format(item_title))

def delete_item(item_id):
    conn = get_connection()
    c = conn.cursor()

    for item_it in c.execute("SELECT Title FROM Items WHERE ItemID=?", (item_id, )).fetchall():
        c.execute("DELETE FROM Items WHERE ItemID=? AND Title=?", (item_id, item_it['Title'], ))
        logger.info("Delete item -- {}.".format(item_it['Title']))

    conn.commit()

def reset_magic(user_id, clf):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM {} WHERE UserID=?".format(clf, ), (user_id, ))

    conn.commit()
    logger.info("Reset {}.".format(clf))

###############################################################################
# Convenience functions.
###############################################################################

def get_user_id(name):
    c = get_cursor()
    user_it = c.execute("SELECT UserID FROM Users WHERE Name=?", (name, )).fetchone()

    user_id = None
    if user_it is not None:
        user_id = user_it['UserID']

    return user_id

def last_updated():
    c = get_cursor()
    timestamp_it = c.execute("SELECT MIN(Updated) FROM Feeds").fetchone()

    timestamp = None
    if timestamp_it is not None:
        timestamp = datetime.strptime(timestamp_it[0], "%Y-%m-%d %H:%M:%S")

    return timestamp

def last_liked(user_id):
    c = get_cursor()
    timestamp_it = c.execute("SELECT MAX(Updated) FROM Like WHERE UserID=?", (user_id, )).fetchone()

    timestamp = None
    if timestamp_it is not None:
        timestamp = datetime.strptime(timestamp_it[0], "%Y-%m-%d %H:%M:%S")

    return timestamp
