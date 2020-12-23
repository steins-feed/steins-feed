#!/usr/bin/env python3

from datetime import datetime
import feedparser
import logging
import sqlalchemy.sql as sql

from . import connect, get_table
from log import get_handler

logger = logging.getLogger('feeds')
logger.setLevel(logging.INFO)
logger.addHandler(get_handler())

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
        for item_it in parse_feed(feed_it):
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
    res = feedparser.parse(feed['Link'])

    try:
        status = res.status
        if status < 300:
            logger.info("{} -- {}.".format(feed['Title'], status))
        elif status < 400:
            logger.warning("{} -- {}.".format(feed['Title'], status))
        else:
            logger.error("{} -- {}.".format(feed['Title'], status))
    except AttributeError:
        if res['items']:
            logger.info("{}.".format(feed['Title']))
        else:
            logger.warning("{}.".format(feed['Title']))

    return res.entries

def read_item(item):
    item_title = read_item_title(item)
    item_link = read_item_link(item)
    item_time = read_item_time(item)
    item_summary = read_item_summary(item)
    return item_title, item_link, item_time, item_summary

def read_item_title(item):
    try:
        item_title = item.title
        return item_title
    except KeyError:
        pass

    logger.error("No title.")
    raise KeyError

def read_item_link(item):
    try:
        item_link = item.link
        return item_link
    except KeyError:
        pass

    try:
        item_link = item.links[0].href
        return item_link
    except KeyError:
        pass

    logger.error("No link for '{}'.".format(read_item_title(item)))
    raise KeyError

def read_item_summary(item):
    return item.summary

def read_item_time(item):
    try:
        item_time = item.published_parsed
        item_time = datetime(*item_time[:6])
        return item_time
    except (KeyError, TypeError, ValueError):
        pass

    try:
        item_time = item.updated_parsed
        item_time = datetime(*item_time[:6])
        return item_time
    except (KeyError, TypeError, ValueError):
        pass

    logger.error("No time for '{}'.".format(read_item_title(item)))
    raise KeyError
