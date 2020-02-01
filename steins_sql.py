#!/usr/bin/env python3

from datetime import datetime
import os
import sqlite3
from sqlite3 import IntegrityError, OperationalError
import time

from steins_log import get_logger

dir_path = os.path.dirname(os.path.abspath(__file__))
DB_NAME = "steins.db"
db_path = dir_path + os.sep + DB_NAME

logger = get_logger()

###############################################################################
# SQLite connection and cursor.
###############################################################################

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

###############################################################################
# Create tables.
###############################################################################

def create_users(users=['nobody']):
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Users (UserID INTEGER PRIMARY KEY, Name TINYTEXT NOT NULL UNIQUE)")
        for user in users:
            c.execute("INSERT INTO Users (Name) VALUES (?)", (user, ))
        conn.commit()
        logger.info("Create Users.")
    except OperationalError:
        pass

def create_feeds():
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Feeds (FeedID INTEGER PRIMARY KEY, Title TEXT NOT NULL UNIQUE, Link TEXT NOT NULL UNIQUE, Language TINYTEXT DEFAULT '', Summary INTEGER DEFAULT 2, Added DATETIME DEFAULT CURRENT_TIMESTAMP, Updated DATETIME DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        logger.info("Create Feeds.")
    except OperationalError:
        pass

def create_items():
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Link TEXT NOT NULL, Published DATETIME NOT NULL, FeedID INTEGER NOT NULL, Summary MEDIUMTEXT, FOREIGN KEY (FeedID) REFERENCES Feeds (FeedID), UNIQUE(Title, Link, Published, FeedID))")
        conn.commit()
        logger.info("Create Items.")
    except OperationalError:
        pass

def create_display():
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Display (UserID INTEGER NOT NULL, FeedID INTEGER NOT NULL, FOREIGN KEY (UserID) REFERENCES Users (UserID), FOREIGN KEY (FeedID) REFERENCES Feeds (FeedID), UNIQUE(UserID, FeedID))")
        conn.commit()
        logger.info("Create Display.")
    except OperationalError:
        pass

def create_like():
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Like (UserID INTEGER NOT NULL, FeedID INTEGER NOT NULL, Score INTEGER NOT NULL, Added DATETIME DEFAULT CURRENT_TIMESTAMP, Updated DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (UserID) REFERENCES Users (UserID), FOREIGN KEY (FeedID) REFERENCES Feeds (FeedID), UNIQUE(UserID, FeedID))")
        conn.commit()
        logger.info("Create Like.")
    except OperationalError:
        pass

###############################################################################
# Modify tables.
###############################################################################

def add_feed(title, link, lang, disp=1, summary=2, user='nobody'):
    c = get_cursor()

    try:
        c.execute("INSERT INTO Feeds (Title, Link, Language, Summary) VALUES (?, ?, ?, ?)", (title, link, lang, summary, ))
        c.execute("INSERT INTO Display ({}) VALUES (?)".format(user), (disp, ))
        logger.info("Add feed -- {}.".format(title))
    except IntegrityError:
        logger.error("Add feed -- {}.".format(title))

def delete_feed(item_id):
    conn = get_connection()
    c = conn.cursor()

    title = c.execute("Select Title FROM Feeds WHERE ItemID=?", (item_id, )).fetchone()[0]
    c.execute("DELETE FROM Feeds WHERE ItemID=?", (item_id, ))
    c.execute("DELETE FROM Display WHERE ItemID=?", (item_id, ))
    logger.info("Delete feed -- {}.".format(title))

    conn.commit()

def add_item(item_title, item_time, item_summary, item_source, item_link):
    c = get_cursor()

    # Punish cheaters.
    if time.strptime(item_time, "%Y-%m-%d %H:%M:%S GMT") > time.gmtime():
        return

    try:
        c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_title, item_time, item_summary, item_source, item_link, ))
        c.execute("INSERT INTO Like DEFAULT VALUES")
        logger.info("Add item -- {}.".format(item_title))
    except IntegrityError:
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
    alter_table_with_users("Display", old_name, new_name)
    alter_table_with_users("Like", old_name, new_name)
    logger.warning("Rename user -- {} to {}.".format(old_name, new_name))

def delete_user(name):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM Users WHERE Name=?", (name, ))
    trim_table_with_users("Display", name)
    trim_table_with_users("Like", name)
    logger.warning("Delete user -- {}.".format(name))
