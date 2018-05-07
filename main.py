#!/usr/bin/env python3

import feedparser
import os.path
import sqlite3
import time

feeds = []
feeds.append("https://www.theguardian.com/uk/technology/rss")
feeds.append("https://www.theatlantic.com/feed/channel/technology/")

# SQLite.
db_name = "steins.db"
db_exists = os.path.isfile(db_name)
conn = sqlite3.connect("steins.db")
c = conn.cursor()
if not db_exists:
    # TODO Table for authors.
    # TODO Table for categories.
    c.execute("CREATE TABLE Items (ItemID INT AUTO_INCREMENT, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Link TEXT NOT NULL, PRIMARY KEY (ItemID))")

# Scrape feeds.
for feed_it in feeds:
    d = feedparser.parse(feed_it)
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=?", (item_it["title"], )).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Link) VALUES (?, ?, ?, ?)", (item_it["title"], time.strftime("%Y-%m-%d %H:%M:%S", item_it["published_parsed"]), item_it["summary"], item_it["link"], ))

# SQLite.
for row_it in c.execute("SELECT Published FROM Items ORDER BY Published DESC"):
    print(row_it)
conn.commit()
conn.close()
