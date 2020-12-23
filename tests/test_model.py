#!/usr/bin/env python3

from model.feeds import read_feeds
from model.xml import read_xml, write_xml

def test_xml_read():
    with open("feeds.xml", 'r') as f:
        read_xml(f)

def test_xml_write():
    with open("tests/feeds.xml", 'w') as f:
        write_xml(f)

def test_feeds():
    read_feeds("The Atlantic")
