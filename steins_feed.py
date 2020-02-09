#!/usr/bin/env python3

import os
dir_path = os.path.dirname(os.path.abspath(__file__))

from steins_log import get_logger
logger = get_logger()
from steins_manager import get_handler
from steins_sql import *

# Scrape feeds.
def steins_read(title_pattern=""):
    conn = get_connection()
    c = conn.cursor()

    for feed_it in c.execute("SELECT * FROM Feeds WHERE Title LIKE ?", ("%" + title_pattern + "%", )).fetchall():
        handler = get_handler(feed_it)
        d = handler.parse(feed_it['Link'])
        try:
            logger.info("{} -- {}.".format(feed_it['Title'], d.status))
        except AttributeError:
            logger.info("{}.".format(feed_it['Title']))

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

# Generate HTML.
def steins_write():
    c = get_cursor()

    dates = c.execute("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM Items ORDER BY Published DESC").fetchall()
    for d_ctr in range(len(dates)):
        with open(dir_path+os.sep+"steins-{}.html".format(d_ctr), 'w') as f:
            f.write(handle_page(page=d_ctr))

def steins_update(title_pattern="", read_mode=True, write_mode=False):
    logger.info("Update feeds.")

    if read_mode:
        steins_read(title_pattern)
    if write_mode:
        steins_write()
