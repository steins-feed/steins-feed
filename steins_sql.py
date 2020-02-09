#!/usr/bin/env python3

from datetime import datetime
import json
import os
import sqlite3

dir_path = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "steins.db"
db_path = dir_path + os.sep + DB_NAME
with open(dir_path + os.sep + "json/steins_magic.json", 'r') as f:
    clf_dict = json.load(f)

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

def create_users(users=None):
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Users (UserID INTEGER PRIMARY KEY, Name TINYTEXT NOT NULL UNIQUE)")
    if users is None:
        c.execute("INSERT INTO Users (Name) VALUES (?)", ('nobody', ))
    else:
        for user_it in users:
            c.execute("INSERT INTO Users (Name) VALUES (?)", (user_it, ))

    conn.commit()
    logger.info("Create Users.")

def create_feeds():
    conn = get_connection()
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS Feeds (FeedID INTEGER PRIMARY KEY, Title TEXT NOT NULL UNIQUE, Link TEXT NOT NULL UNIQUE, Language TINYTEXT, Summary INTEGER DEFAULT 2, Added TIMESTAMP DEFAULT CURRENT_TIMESTAMP, Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")

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
        c.execute("CREATE TABLE IF NOT EXISTS {} (UserID INTEGER NOT NULL, ItemID INTEGER NOT NULL, Score FLOAT NOT NULL, Added TIMESTAMP DEFAULT CURRENT_TIMESTAMP, Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (UserID) REFERENCES Users (UserID) ON UPDATE CASCADE ON DELETE CASCADE, FOREIGN KEY (ItemID) REFERENCES Items (ItemID) ON UPDATE CASCADE ON DELETE CASCADE, UNIQUE(UserID, ItemID))".format(clf_dict[clf_it]['table']))

    conn.commit()
    logger.info("Create Magic.")

###############################################################################
# Modify tables.
###############################################################################

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

    for clf_it in clf_dict:
        c.execute("DELETE FROM {} WHERE UserID=?".format(clf_dict[clf_it]['table'], ), (user_id, ))

    conn.commit()
    logger.info("Reset {}.".format(clf))

###############################################################################
# Convenience functions.
###############################################################################

def last_updated():
    c = get_cursor()
    timestamp_it = c.execute("SELECT MIN(Updated) FROM Feeds").fetchone()

    timestamp = datetime.fromtimestamp(0)
    if timestamp_it[0] is not None:
        timestamp = datetime.strptime(timestamp_it[0], "%Y-%m-%d %H:%M:%S")

    return timestamp

def last_liked(user_id):
    c = get_cursor()
    timestamp_it = c.execute("SELECT MAX(Updated) FROM Like WHERE UserID=?", (user_id, )).fetchone()

    timestamp = datetime.fromtimestamp(0)
    if timestamp_it[0] is not None:
        timestamp = datetime.strptime(timestamp_it[0], "%Y-%m-%d %H:%M:%S")

    return timestamp
