#!/usr/bin/env python3

import os.path
import feedparser
import sqlite3

feeds = []
feeds.append("https://www.theguardian.com/uk/technology/rss")
feeds.append("https://www.theatlantic.com/feed/channel/technology/")

# SQLite.
db_name = "steins.db"
db_exists = os.path.isfile(db_name)
conn = sqlite3.connect("steins.db")
c = conn.cursor()
if not db_exists:
    # TODO Check for uniqueness.
    # TODO Table for authors.
    # TODO Table for categories.
    c.execute("CREATE TABLE Items (ItemID INT AUTO_INCREMENT, Title TEXT NOT NULL, Description MEDIUMTEXT, Link TEXT NOT NULL, PRIMARY KEY (ItemID))")

# Guardian.
for feed_it in feeds:
    d = feedparser.parse(feed_it)
    for item_it in d['items']:
        c.execute("INSERT INTO Items (Title, Description, Link) VALUES (?, ?, ?)", (item_it["title"], item_it["description"], item_it["link"]))

# SQLite.
for row_it in c.execute("SELECT Title FROM Items"):
    print(row_it)
conn.commit()
conn.close()
