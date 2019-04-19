#!/usr/bin/env python3

import os
import sqlite3
import time

DB_NAME = "steins.db"
dir_path = os.path.dirname(os.path.abspath(__file__))
db_path = dir_path + os.sep + DB_NAME

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
    return connection

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
