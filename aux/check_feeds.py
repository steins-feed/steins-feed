#!/usr/bin/env python3

import glob
from lxml import etree
import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_sql import *
conn = get_connection()
c = get_cursor()

feeds_xml = []
for f_it in glob.glob(dir_path + os.sep + "feeds.d/*"):
    root = etree.parse(f_it)
    for feed_it in root.xpath("./feed"):
        feeds_xml.append([feed_it.xpath("./title")[0].text, feed_it.xpath("./link")[0].text, feed_it.xpath("./lang")[0].text])
print(len(feeds_xml))

feeds_sql = []
for feed_it in c.execute("SELECT * FROM Feeds"):
    feeds_sql.append([feed_it['Title'], feed_it['Link'], feed_it['Language']])
print(len(feeds_sql))

for feed_it in feeds_xml:
    if feed_it not in feeds_sql:
        print(feed_it)

for feed_it in feeds_sql:
    if feed_it not in feeds_xml:
        print(feed_it)
