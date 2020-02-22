#!/usr/bin/env python3

import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_sql import *

# Create tables.
create_users()
create_feeds()
create_items()
create_display()
create_tags()
create_like()
create_magic()

close_connection()
