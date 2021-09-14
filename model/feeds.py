#!/usr/bin/env python3

import datetime
import logging
import time

import feedparser
from sqlalchemy import func, sql

import log

from . import get_connection, get_table

# Logger.
logger = log.Logger(__name__, logging.INFO)

def read_feeds(title_pattern=None):
    t_feeds = get_table("Feeds")
    t_items = get_table("Items")

    q = sql.select([t_feeds])
    if title_pattern:
        q = q.where(t_feeds.c.Title.like(f"%{title_pattern}%"))
    q = q.order_by(sql.collate(t_feeds.c.Title, "NOCASE"))

    with get_connection() as conn:
        feeds = conn.execute(q).fetchall()

    for feed_it in feeds:
        rows = []
        for item_it in parse_feed(feed_it).entries:
            try:
                row_it = read_item(item_it)
            except AttributeError:
                continue

            row_it["FeedID"] = feed_it["FeedID"]
            rows.append(row_it)

        q = t_items.insert()
        q = q.prefix_with("OR IGNORE", dialect="sqlite")

        with get_connection() as conn:
            conn.execute(q, rows)

        q = (t_feeds.update()
                    .values(Updated=func.now())
                    .where(t_feeds.c.FeedID == feed_it["FeedID"]))

        with get_connection() as conn:
            conn.execute(q)

def parse_feed(feed, timeout=1):
    try:
        res = feedparser.parse(feed["Link"])

        status = res.status
        if status < 300:
            logger.info(f"{feed['Title']} -- {status}.")
        elif status < 400:
            logger.warning(f"{feed['Title']} -- {status}.")
        elif status == 429 and timeout < 5:     # too many requests
            logger.warning(f"{feed['Title']} -- {status} (timeout = {timeout} sec).")
            time.sleep(timeout)
            parse_feed(feed, 2 * timeout)
        else:
            logger.error(f"{feed['Title']} -- {status}.")
    except OSError as e:
        logger.error(f"{feed['Title']} -- {e}.")
        res = feedparser.util.FeedParserDict(entries=[])
    except AttributeError:
        if res.entries:
            logger.info(f"{feed['Title']}.")
        else:
            logger.warning(f"{feed['Title']}.")

    return res

def read_item(item):
    return {
        "Title": read_item_title(item),
        "Link": read_item_link(item),
        "Published": read_item_time(item),
        "Summary": read_item_summary(item),
    }

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

    logger.error(f"No link for '{read_item_title(item)}'.")
    raise AttributeError

def read_item_summary(item):
    return item.summary

def read_item_time(item):
    try:
        item_time = item.published_parsed
        item_time = datetime.datetime(*item_time[:6])
        return item_time
    except (AttributeError, TypeError):
        pass

    try:
        item_time = item.updated_parsed
        item_time = datetime.datetime(*item_time[:6])
        return item_time
    except (AttributeError, TypeError):
        pass

    logger.error(f"No time for '{read_item_title(item)}'.")
    raise AttributeError
