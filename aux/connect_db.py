#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect("steins.db", detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.row_factory = sqlite3.Row
c = conn.cursor()
