#!/usr/bin/env python3

import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_sql import get_cursor, delete_item

c = get_cursor()
for item_id in c.execute("SELECT ItemID FROM Items WHERE NOT Source IN (SELECT DISTINCT Title FROM Feeds)").fetchall():
    delete_item(item_id[0])
