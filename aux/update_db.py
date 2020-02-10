#!/usr/bin/env python3

import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_feed import steins_read
from steins_sql import get_connection
conn = get_connection()
from steins_log import get_logger
logger = get_logger()

title_pattern = ""
if len(sys.argv) > 1:
    title_pattern = sys.argv[1]

logger.info("Update feeds.")
steins_read(title_pattern)

conn.close()
