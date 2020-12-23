#!/usr/bin/env python3

from sqlalchemy import func, sql

from model import get_connection, get_table
from model.feeds import read_feeds
from model.xml import read_xml, write_xml

def test_xml_read():
    conn = get_connection()
    feeds = get_table('Feeds')

    with open("feeds.xml", 'r') as f:
        read_xml(f)

    q = sql.select([func.count()]).select_from(feeds)
    res = conn.execute(q).fetchone()
    assert(res[0] > 0)

def test_xml_write():
    with open("tests/feeds.xml", 'w') as f:
        write_xml(f)

def test_feeds():
    conn = get_connection()
    items = get_table('Items')

    read_feeds("The Atlantic")

    q = sql.select([func.count()]).select_from(items)
    res = conn.execute(q).fetchone()
    assert(res[0] > 0)
