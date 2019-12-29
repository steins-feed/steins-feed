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

def create_table_with_users(name, users=['nobody'], vals=[0]):
    conn = get_connection()
    c = conn.cursor()

    statement = "CREATE TABLE {} (ItemID INTEGER PRIMARY KEY".format(name)
    for user_ct in range(len(users)):
        statement += ", {} INTEGER DEFAULT {}".format(users[user_ct], vals[user_ct])
    statement += ")"
    c.execute(statement)
    conn.commit()

def alter_table_with_users(table, old_name, new_name):
    conn = get_connection()
    c = conn.cursor()

    table_info = c.execute("PRAGMA table_info({})".format(table)).fetchall()[1:]
    e_old = [e for e in table_info if e[1] == old_name][0]
    val_old = e_old[4]
    table_info.remove(e_old)
    name_list = [e[1] for e in table_info]
    old_name_list = name_list + [old_name]
    new_name_list = name_list + [new_name]
    val_list = [e[4] for e in table_info] + [val_old]

    c.execute("ALTER TABLE {0} RENAME TO {0}_old".format(table))
    create_table_with_users(table, new_name_list, val_list)
    c.execute("INSERT INTO {0} (ItemID, {1}) SELECT ItemID, {2} FROM {0}_old".format(table, ", ".join(new_name_list), ", ".join(old_name_list)))
    c.execute("DROP TABLE {}_old".format(table))

    conn.commit()

def trim_table_with_users(table, name):
    conn = get_connection()
    c = conn.cursor()

    table_info = c.execute("PRAGMA table_info({})".format(table)).fetchall()
    table_info = [e for e in table_info[1:] if not e[1] == name]
    name_list = [e[1] for e in table_info]
    val_list = [e[4] for e in table_info]

    c.execute("ALTER TABLE {0} RENAME TO {0}_old".format(table))
    create_table_with_users(table, name_list, val_list)
    c.execute("INSERT INTO {0} (ItemID, {1}) SELECT ItemID, {1} FROM {0}_old".format(table, ", ".join(name_list)))
    c.execute("DROP TABLE {}_old".format(table))

    conn.commit()

def create_feeds():
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Feeds (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Link TEXT NOT NULL, Language TEXT DEFAULT '', Summary INTEGER DEFAULT 2, UNIQUE(Title, Link))")
        conn.commit()
        logger.warning("Create Feeds.")
    except OperationalError:
        pass

def create_display(users=['nobody'], vals=[1]):
    try:
        create_table_with_users("Display", users, vals)
        logger.warning("Create Display.")
    except OperationalError:
        pass

def create_items():
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Items (ItemID INTEGER PRIMARY KEY, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, UNIQUE(Title, Published, Source, Link))")
        conn.commit()
        logger.warning("Create Items.")
    except OperationalError:
        pass

def create_like(users=['nobody'], vals=[0]):
    try:
        create_table_with_users("Like", users, vals)
        logger.warning("Create Like.")
    except OperationalError:
        pass

def create_users(users=['nobody']):
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Users (ItemID INTEGER PRIMARY KEY, Name TINYTEXT NOT NULL UNIQUE)")
        for user in users:
            c.execute("INSERT INTO Users (Name) VALUES (?)", (user, ))
        conn.commit()
        logger.warning("Create Users.")
    except OperationalError:
        pass

def create_updates():
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("CREATE TABLE Updates (ItemID INTEGER PRIMARY KEY, Record TIMESTAMP NOT NULL)")
        conn.commit()
        logger.warning("Create Updates.")
    except OperationalError:
        pass

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
