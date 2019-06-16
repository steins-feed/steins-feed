#!/usr/bin/env python3

from steins_sql import get_cursor, delete_item

c = get_cursor()
for item_id in c.execute("SELECT ItemID FROM Items WHERE NOT Source IN (SELECT DISTINCT Title FROM Feeds)").fetchall():
    delete_item(item_id)
