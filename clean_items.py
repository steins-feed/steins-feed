#!/usr/bin/env python3

from steins_sql import get_cursor, delete_item

c = get_cursor()

feeds = [e[0] for e in c.execute("SELECT DISTINCT Title FROM Feeds").fetchall()]
items = c.execute("SELECT * FROM Items").fetchall()

for item_it in items:
    if not item_it['Source'] in feeds:
        delete_item(item_it['ItemID'])
