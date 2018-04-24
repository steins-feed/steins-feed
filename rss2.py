#!/usr/bin/env python3

import feedparser

d = feedparser.parse("https://www.theguardian.com/uk/technology/rss")
for item_it in d['items']:
    print(item_it['title'])
