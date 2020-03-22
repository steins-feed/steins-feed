#!/usr/bin/env python3

import os
dir_path = os.path.dirname(os.path.abspath(__file__))
import time

from steins_log import get_logger
logger = get_logger()
from steins_manager import SteinsHandler
from steins_sql import get_connection, get_cursor, add_item

# Scrape feeds.
def steins_read(title_pattern=""):
    conn = get_connection()
    c = get_cursor()

    handler = SteinsHandler()
    parsers = c.execute("SELECT * FROM Parsers").fetchall()
    parsers = dict([(p_it[0], p_it) for p_it in parsers])
    for feed_it in c.execute("SELECT * FROM Feeds WHERE Title LIKE ? ORDER BY Title", ("%" + title_pattern + "%", )).fetchall():
        patterns = parsers.get(feed_it['ParserID'], None)
        d, status = handler.parse(feed_it['Link'], patterns)
        if status < 0:
            logger.warning("{}.".format(feed_it['Title']))
        elif status < 300:
            logger.info("{} -- {}.".format(feed_it['Title'], d.status))
        elif status < 400:
            logger.warning("{} -- {}.".format(feed_it['Title'], d.status))
        else:
            logger.error("{} -- {}.".format(feed_it['Title'], d.status))

        for item_it in d['items']:
            try:
                item_title = handler.read_title(item_it)
                item_link = handler.read_link(item_it)
                item_time = handler.read_time(item_it)
                item_summary = handler.read_summary(item_it)
            except KeyError:
                continue

            add_item(item_title, item_link, item_time, feed_it['FeedID'], item_summary)

        c.execute("UPDATE Feeds SET Updated=datetime('now') WHERE FeedID=?", (feed_it['FeedID'], ))
        conn.commit()

        if feed_it['Pause'] > 0:
            time.sleep(feed_it['Pause'])

# Generate HTML.
def steins_write():
    c = get_cursor()

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items ORDER BY Published DESC").fetchall()
    for d_ctr in range(len(dates)):
        with open(dir_path+os.sep+"steins-{}.html".format(d_ctr), 'w') as f:
            f.write(handle_page(page=d_ctr))
