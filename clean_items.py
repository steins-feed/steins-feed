#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect("steins.db")
c = conn.cursor()

feeds = c.execute("SELECT Title FROM Feeds").fetchall()
feeds = [e[0] for e in feeds]
items = c.execute("SELECT * FROM Items").fetchall()

for item_it in items:
    if not item_it[4] in feeds:
        print("Delete \"{}\" ({}).".format(item_it[1], item_it[4]))
        c.execute("DELETE FROM Items WHERE ItemID=?", (item_it[0], ))

conn.commit()
