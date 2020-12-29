#!/usr/bin/env python3

from datetime import datetime
import feedparser
import logging
from sqlalchemy import func, sql
import time

from . import get_connection, get_table
from log import get_handler

logger = logging.getLogger('feeds')
logger.setLevel(logging.INFO)
logger.addHandler(get_handler())

def read_feeds(title_pattern=None):
    conn = get_connection()
    feeds = get_table('Feeds')
    items = get_table('Items')

    q = sql.select([feeds])
    if title_pattern:
        q = q.where(feeds.c.Title.like("%{}%".format(title_pattern)))
    q = q.order_by(sql.collate(feeds.c.Title, 'NOCASE'))

    row_keys = [
        'Title',
        'Link',
        'Published',
        'Summary'
    ]

    for feed_it in conn.execute(q):
        try:
            item_ls = parse_feed(feed_it).entries
        except OSError as e:
            logger.error("{} -- {}.".format(feed_it['Title'], e))
            continue

        rows = []
        for item_it in item_ls:
            try:
                row_values = read_item(item_it)
            except AttributeError:
                continue
            row_it = dict(zip(row_keys, row_values))
            row_it['FeedID'] = feed_it['FeedID']
            rows.append(row_it)

        q = items.insert()
        q = q.prefix_with("OR IGNORE", dialect='sqlite')
        conn.execute(q, rows)

        q = (feeds.update()
                  .values(Updated=func.now())
                  .where(feeds.c.FeedID == feed_it['FeedID']))
        conn.execute(q)

def parse_feed(feed, timeout=1):
    res = feedparser.parse(feed['Link'])
    try:
        status = res.status
        if status < 300:
            logger.info("{} -- {}.".format(feed['Title'], status))
        elif status < 400:
            logger.warning("{} -- {}.".format(feed['Title'], status))
        elif status == 429 and timeout < 5: # too many requests
            logger.warning("{} -- {} (timeout = {} sec).".format(feed['Title'], status, timeout))
            time.sleep(timeout)
            parse_feed(feed, 2 * timeout)
        else:
            logger.error("{} -- {}.".format(feed['Title'], status))
    except AttributeError:
        if res.entries:
            logger.info("{}.".format(feed['Title']))
        else:
            logger.warning("{}.".format(feed['Title']))

    return res

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
    except AttributeError:
        pass

    logger.error("No title.")
    raise AttributeError

def read_item_link(item):
    try:
        item_link = item.link
        return item_link
    except AttributeError:
        pass

    try:
        item_link = item.links[0].href
        return item_link
    except AttributeError:
        pass

    logger.error("No link for '{}'.".format(read_item_title(item)))
    raise AttributeError

def read_item_summary(item):
    return item.summary

def read_item_time(item):
    try:
        item_time = item.published_parsed
        item_time = datetime(*item_time[:6])
        return item_time
    except (AttributeError, TypeError):
        pass

    try:
        item_time = item.updated_parsed
        item_time = datetime(*item_time[:6])
        return item_time
    except (AttributeError, TypeError):
        pass

    logger.error("No time for '{}'.".format(read_item_title(item)))
    raise AttributeError
