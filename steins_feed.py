#!/usr/bin/env python3

import feedparser
import os.path
import sqlite3
import time

# Scrape feeds.
def steins_read(c):
    # The Guardian.
    d = feedparser.parse("https://www.theguardian.com/uk/technology/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "Guardian Technology", item_it['link'], ))
    
    # The Atlantic.
    d = feedparser.parse("https://www.theatlantic.com/feed/channel/technology/")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['content'][1]['value'], "Atlantic Technology", item_it['link'], ))
    
    # WIRED Business.
    d = feedparser.parse("https://www.wired.com/feed/category/business/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Business", item_it['link'], ))
    
    # WIRED Culture.
    d = feedparser.parse("https://www.wired.com/feed/category/culture/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Culture", item_it['link'], ))
    
    # WIRED Ideas.
    d = feedparser.parse("https://www.wired.com/feed/category/ideas/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Ideas", item_it['link'], ))
    
    # WIRED Science.
    d = feedparser.parse("https://www.wired.com/feed/category/science/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Science", item_it['link'], ))
    
    # WIRED Security.
    d = feedparser.parse("https://www.wired.com/feed/category/security/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Security", item_it['link'], ))
    
    # WIRED Transportation.
    d = feedparser.parse("https://www.wired.com/feed/category/transportation/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Transportation", item_it['link'], ))
    
    # WIRED Backchannel.
    d = feedparser.parse("https://www.wired.com/feed/category/backchannel/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Backchannel", item_it['link'], ))
    
    # WIRED Guides.
    d = feedparser.parse("https://www.wired.com/feed/tag/wired-guide/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Guide", item_it['link'], ))
    
    # WIRED Photo.
    d = feedparser.parse("https://www.wired.com/feed/category/photo/latest/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Photo", item_it['link'], ))
    
    # WIRED.
    d = feedparser.parse("https://www.wired.com/feed/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED", item_it['link'], ))
    
    # XKCD.
    d = feedparser.parse("https://www.xkcd.com/rss.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "XKCD", item_it['link'], ))

# Generate HTML.
def steins_write(c):
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

def steins_update():
    db_name = "steins.db"
    db_exists = os.path.isfile(db_name)
    conn = sqlite3.connect("steins.db")
    c = conn.cursor()
    if not db_exists:
        c.execute("CREATE TABLE Items (ItemID INT AUTO_INCREMENT, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, PRIMARY KEY (ItemID))")
    steins_read(c)
    steins_write(c)
    conn.commit()
    conn.close()
