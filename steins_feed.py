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
    
    # The Atlantic -- Crazy/Genius.
    d = feedparser.parse("https://feeds.megaphone.fm/crazygenius")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['content'][0]['value'], "Atlantic Crazy/Genius", item_it['links'][0]['href'], ))

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
    
    ## WIRED Photo.
    #d = feedparser.parse("https://www.wired.com/feed/category/photo/latest/rss")
    #for item_it in d['items']:
    #    if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
    #        c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "WIRED Photo", item_it['link'], ))
    
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

    # Chalkdust.
    d = feedparser.parse("http://chalkdustmagazine.com/feed/")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "Chalkdust", item_it['link'], ))

    # Gates Notes.
    d = feedparser.parse("https://www.gatesnotes.com/rss")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(item_it['published'], "%m/%d/%Y %I:%M:%S %p")))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(item_it['published'], "%m/%d/%Y %I:%M:%S %p")), item_it['summary'], "Gates Notes", item_it['link'], ))

    # TED Ideas.
    d = feedparser.parse("https://ideas.ted.com/feed/")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "TED Ideas", item_it['link'], ))

    # Quanta Magazine.
    d = feedparser.parse("https://api.quantamagazine.org/feed/")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "Quanta Magazine", item_it['link'], ))

    # Scientific American.
    d = feedparser.parse("http://rss.sciam.com/ScientificAmerican-Global")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['published_parsed']), item_it['summary'], "Scientific American", item_it['link'], ))

    # The Register Data Centre.
    d = feedparser.parse("https://www.theregister.co.uk/data_centre/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Data Centre", item_it['link'], ))

    # The Register Software.
    d = feedparser.parse("https://www.theregister.co.uk/software/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Software", item_it['link'], ))

    # The Register Security.
    d = feedparser.parse("https://www.theregister.co.uk/security/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Security", item_it['link'], ))

    # The Register Transformation.
    d = feedparser.parse("https://www.theregister.co.uk/transformation/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Transformation", item_it['link'], ))

    # The Register Devops.
    d = feedparser.parse("https://www.theregister.co.uk/devops/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Devops", item_it['link'], ))

    # The Register Business.
    d = feedparser.parse("https://www.theregister.co.uk/business/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Business", item_it['link'], ))

    # The Register Personal Tech.
    d = feedparser.parse("https://www.theregister.co.uk/personal_tech/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Personal Tech", item_it['link'], ))

    # The Register Science.
    d = feedparser.parse("https://www.theregister.co.uk/science/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Science", item_it['link'], ))

    # The Register Emergent Tech.
    d = feedparser.parse("https://www.theregister.co.uk/emergent_tech/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Emergent Tech", item_it['link'], ))

    # The Register Bootnotes.
    d = feedparser.parse("https://www.theregister.co.uk/bootnotes/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register Bootnotes", item_it['link'], ))

    # The Register.
    d = feedparser.parse("https://www.theregister.co.uk/headlines.atom")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "The Register", item_it['link'], ))

    # Heise Developer.
    d = feedparser.parse("https://www.heise.de/developer/rss/news-atom.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise Developer", item_it['link'], ))

    # Heise Security.
    d = feedparser.parse("https://www.heise.de/security/rss/news-atom.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise Security", item_it['link'], ))

    # Heise c't.
    d = feedparser.parse("https://www.heise.de/ct/rss/artikel-atom.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise c't", item_it['link'], ))

    # Heise Make.
    d = feedparser.parse("https://www.heise.de/make/rss/hardware-hacks-atom.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise Make", item_it['link'], ))

    # Heise iX.
    d = feedparser.parse("https://www.heise.de/iX/rss/news-atom.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise iX", item_it['link'], ))

    # Heise Technology Review.
    d = feedparser.parse("https://www.heise.de/tr/rss/news-atom.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise Technology Review", item_it['link'], ))

    # Heise Telepolis.
    d = feedparser.parse("https://www.heise.de/tp/rss/news-atom.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise Telepolis", item_it['link'], ))

    # Heise TechStage.
    d = feedparser.parse("https://www.techstage.de/rss.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise TechStage", item_it['link'], ))

    # Heise.
    d = feedparser.parse("https://www.heise.de/newsticker/heise-atom.xml")
    for item_it in d['items']:
        if c.execute("SELECT COUNT(*) FROM Items WHERE Title=? AND Published=?", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']))).fetchone()[0] == 0:
            c.execute("INSERT INTO Items (Title, Published, Summary, Source, Link) VALUES (?, ?, ?, ?, ?)", (item_it['title'], time.strftime("%Y-%m-%d %H:%M:%S", item_it['updated_parsed']), item_it['summary'], "Heise", item_it['link'], ))

# Generate HTML.
def steins_write(c):
    dir_name = os.path.dirname(os.path.abspath(__file__))
    times = c.execute("SELECT Published FROM Items")
    dates = sorted(list(set([t_it[0][:10] for t_it in times])), reverse=True)
    f_list = dict()

    d_cnt = 0
    for d_it in dates:
        f = open(dir_name+os.sep+"steins-{}.html".format(d_cnt), 'w')

        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n")
        f.write("<head>\n")
        f.write("<meta charset=\"UTF-8\">")
        f.write("<title>Stein's Feed</title>\n")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write("<h1>{}</h1>\n".format(time.strftime("%A, %d %B %Y", time.strptime(d_it, "%Y-%m-%d"))))
        f.write("<hr>\n")

        f_list[d_it] = f
        d_cnt += 1

    for row_it in c.execute("SELECT * FROM Items ORDER BY Published DESC"):
        f = f_list[row_it[2][:10]]

        f.write("<h2><a href=\"{}\">{}</a></h2>\n".format(row_it[5], row_it[1]))
        f.write("<p>Source: {}. Published: {}</p>".format(row_it[4], row_it[2]))
        f.write("{}".format(row_it[3]))
        f.write("<hr>\n")

    d_cnt = 0
    d_len = len(dates)
    for d_it in dates:
        f = f_list[d_it]

        f.write("<form>\n")
        if not d_cnt == 0:
            f.write("<input type=\"submit\" formaction=\"/steins-{}.html\" value=\"Previous\">\n".format(d_cnt-1))
        if not d_cnt == d_len-1:
            f.write("<input type=\"submit\" formaction=\"/steins-{}.html\" value=\"Next\">\n".format(d_cnt+1))
        f.write("</form>\n")
        f.write("</body>\n")
        f.write("</html>\n")
        f.close()

        d_cnt += 1

def steins_update():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    db_name = dir_name + os.sep + "steins.db"
    db_exists = os.path.isfile(db_name)
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    if not db_exists:
        c.execute("CREATE TABLE Items (ItemID INT AUTO_INCREMENT, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, PRIMARY KEY (ItemID))")
    steins_read(c)
    steins_write(c)
    conn.commit()
    conn.close()
