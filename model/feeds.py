#!/usr/bin/env python3

from datetime import datetime
import feedparser
from lxml import etree
import sqlalchemy.sql as sql

from .database import connect, get_table
from .schema import LANG

def read_xml(f):
    conn = connect()
    feeds = get_table('Feeds')

    tree = etree.parse(f)
    root = tree.getroot()
    ins_rows = []

    for feed_it in root.xpath("feed"):
        title = feed_it.xpath("title")[0].text
        link = feed_it.xpath("link")[0].text
        lang = LANG(feed_it.xpath("lang")[0].text).name

        ins_rows.append(dict(zip(
                ['Title', 'Link', 'Language'],
                [title, link, lang]
        )))

    ins = feeds.insert()
    ins = ins.prefix_with("OR IGNORE", dialect='sqlite')
    conn.execute(ins, ins_rows)

def write_xml(f):
    conn = connect()
    feeds = get_table('Feeds')

    root = etree.Element("root")
    for row_it in conn.execute(sql.select([feeds])):
        title_it = etree.Element("title")
        title_it.text = row_it['Title']
        link_it = etree.Element("link")
        link_it.text = row_it['Link']
        lang_it = etree.Element("lang")
        lang_it.text = row_it['Language']

        feed_it = etree.Element("feed")
        feed_it.append(title_it)
        feed_it.append(link_it)
        feed_it.append(lang_it)
        root.append(feed_it)

    s = etree.tostring(root, xml_declaration=True, pretty_print=True)
    f.write(s.decode())

def read_feeds():
    conn = connect()
    feeds = get_table('Feeds')
    items = get_table('Items')

    q = (sql
        .select([feeds])
        .order_by(sql.collate(feeds.c.Title, 'NOCASE'))
    )
    row_keys = [
        'Title',
        'Link',
        'Published',
        'Summary'
    ]

    for feed_it in conn.execute(q):
        ins_rows = []

        d = parse_feed(feed_it)
        for item_it in d['items']:
            try:
                row_values = read_item(item_it)
            except KeyError:
                continue
            ins_row = dict(zip(row_keys, row_values))
            ins_row['FeedID'] = feed_it['FeedID']
            ins_rows.append(ins_row)

        ins = items.insert()
        ins = ins.prefix_with("OR IGNORE", dialect='sqlite')
        conn.execute(ins, ins_rows)

def parse_feed(feed):
    return feedparser.parse(feed['Link'])

def read_item(item):
    item_title = read_item_title(item)
    item_link = read_item_link(item)
    item_time = read_item_time(item)
    item_summary = read_item_summary(item)
    return item_title, item_link, item_time, item_summary

def read_item_title(item):
    try:
        item_title = item['title']
        return item_title
    except KeyError:
        pass

    #logger.error("No title.")
    raise KeyError

def read_item_link(item):
    try:
        item_link = item['link']
        return item_link
    except KeyError:
        pass

    try:
        item_link = item['links'][0]['href']
        return item_link
    except KeyError:
        pass

    #logger.error("No link for '{}'.".format(self.read_title(item)))
    raise KeyError

def read_item_summary(item):
    return item['summary']

def read_item_time(item):
    try:
        item_time = item['published_parsed']
        item_time = datetime(*item_time[:6])
        return item_time
    except (KeyError, TypeError, ValueError):
        pass

    try:
        item_time = item['updated_parsed']
        item_time = datetime(*item_time[:6])
        return item_time
    except (KeyError, TypeError, ValueError):
        pass

    #logger.error("No time for '{}'.".format(self.read_title(item)))
    raise KeyError
