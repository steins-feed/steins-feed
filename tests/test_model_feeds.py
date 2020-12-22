#!/usr/bin/env python3

from model.feeds import read_xml, write_xml, read_feeds

with open("feeds.xml", 'r') as f:
    read_xml(f)
with open("tests/feeds.xml", 'w') as f:
    write_xml(f)
read_feeds()
