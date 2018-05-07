#!/usr/bin/env python3

import os.path
import feedparser
import sqlite3

# SQLite.
db_name = "steins.db"
db_exists = os.path.isfile(db_name)
conn = sqlite3.connect("steins.db")
c = conn.cursor()
if not db_exists:
    # TODO Check for uniqueness.
    # TODO Table for authors.
    # TODO Table for categories.
    #c.execute("CREATE TABLE Items (ItemID INT AUTO_INCREMENT, Title TEXT NOT NULL, Creator TEXT NOT NULL, Date DATETIME NOT NULL, Description MEDIUMTEXT, Link TEXT NOT NULL, PRIMARY KEY (ItemID))")
    c.execute("CREATE TABLE Items (ItemID INT AUTO_INCREMENT, Title TEXT NOT NULL, Creator TEXT NOT NULL, Description MEDIUMTEXT, Link TEXT NOT NULL, PRIMARY KEY (ItemID))")

# Guardian.
d = feedparser.parse("https://www.theguardian.com/uk/technology/rss")
for item_it in d['items']:
    #c.execute("INSERT INTO Items (Title, Creator, Date, Description, Link) VALUES (?, ?, ?, ?, ?)", (item_it["title"], item_it["dc:creator"], item_it["dc:date"], item_it["description"], item_it["link"]))
    c.execute("INSERT INTO Items (Title, Creator, Description, Link) VALUES (?, ?, ?, ?)", (item_it["title"], item_it["author"], item_it["description"], item_it["link"]))

# SQLite.
for row_it in c.execute("SELECT Title FROM Items"):
    print(row_it)
conn.close()
