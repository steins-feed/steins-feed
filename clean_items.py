#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect("steins.db")
c = conn.cursor()

feeds = c.execute("SELECT Title FROM Feeds").fetchall()
feeds = [e['ItemID'] for e in feeds]
items = c.execute("SELECT * FROM Items").fetchall()

for item_it in items:
    if not item_it['Source'] in feeds:
        print("Delete \"{}\" ({}).".format(item_it['Title'], item_it['Source']))
        c.execute("DELETE FROM Items WHERE ItemID=?", (item_it['ItemID'], ))

conn.commit()
