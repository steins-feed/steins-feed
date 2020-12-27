#!/usr/bin/env python3

import glob
from lxml import etree
import os

from model.schema import Language
from model.utils.all import all_feeds

feeds_xml = []
for f_it in glob.glob("feeds.d/*.xml"):
    root = etree.parse(f_it)
    for feed_it in root.xpath("./feed"):
        feeds_xml.append((
                feed_it.xpath("./title")[0].text,
                feed_it.xpath("./link")[0].text,
                Language(feed_it.xpath("./lang")[0].text).name
        ))
print(len(feeds_xml))

feeds_sql = []
for feed_it in all_feeds():
    feeds_sql.append((
            feed_it['Title'],
            feed_it['Link'],
            feed_it['Language']))
print(len(feeds_sql))

for feed_it in feeds_xml:
    if feed_it not in feeds_sql:
        print(feed_it)

for feed_it in feeds_sql:
    if feed_it not in feeds_xml:
        print(feed_it)
