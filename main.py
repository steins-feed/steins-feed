#!/usr/bin/env python3

import feedparser
import os.path
import sqlite3
import time

feeds = []
feeds.append("https://www.theguardian.com/uk/technology/rss")
feeds.append("https://www.theatlantic.com/feed/channel/technology/")

# Scrape feeds.
db_name = "steins.db"
db_exists = os.path.isfile(db_name)
conn = sqlite3.connect("steins.db")
c = conn.cursor()
if not db_exists:
    # TODO Table for authors.
    # TODO Table for categories.
    # TODO Denote source.
    c.execute("CREATE TABLE Items (ItemID INT AUTO_INCREMENT, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, PRIMARY KEY (ItemID))")

d = feedparser.parse("https://www.theguardian.com/uk/technology/rss")
for item_it in d['items']:
    if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
        c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "Guardian Technology", item_it['link'], ))

d = feedparser.parse("https://www.theatlantic.com/feed/channel/technology/")
for item_it in d['items']:
    if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
        c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['content'][1]['value'], "Atlantic Technology", item_it['link'], ))

conn.commit()
conn.close()

# Generate HTML.
conn = sqlite3.connect("steins.db")
c = conn.cursor()

f = open("steins.html", 'w')
f.write("<!DOCTYPE html>\n")
f.write("<html>\n")
f.write("<head>\n")
f.write("<meta charset=\"UTF-8\">")
f.write("<title>Stein's Feed</title>\n")
f.write("</head>\n")
f.write("<body>\n")
for row_it in c.execute("SELECT * FROM Items ORDER BY Published DESC"):
    f.write("<h2><a href=\"{}\">{}</a></h2>\n".format(row_it[5], row_it[1]))
    f.write("<p>Source: {}. Published: {}</p>".format(row_it[4], row_it[2]))
    f.write("{}".format(row_it[3]))
    f.write("<hr>\n")
f.write("</body>\n")
f.write("</html>\n")
f.close()

conn.commit()
conn.close()
