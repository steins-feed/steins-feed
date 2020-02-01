#!/usr/bin/env python3

import os
import sqlite3
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

file_name = "steins.db"
if len(sys.argv) > 1:
    file_name = sys.argv[1]

conn = sqlite3.connect(file_name, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
conn.row_factory = sqlite3.Row
c = conn.cursor()
