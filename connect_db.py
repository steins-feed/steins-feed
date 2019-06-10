#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect("steins.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()
