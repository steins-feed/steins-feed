#!/usr/bin/env python3

import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_sql import get_connection, get_cursor

conn = get_connection()
c = get_cursor()

c.execute("INSERT OR IGNORE INTO Users (Name) VALUES (?)", ('nobody', ))
c.execute("INSERT OR IGNORE INTO Display SELECT (SELECT UserID FROM Users WHERE Name=?), FeedID FROM Feeds", ('nobody', ))

conn.commit()
