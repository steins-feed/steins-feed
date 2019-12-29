#!/usr/bin/env python3

import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_sql import create_feeds, create_display, create_items, create_like, create_users, create_updates

# Create tables.
create_feeds()
create_display(users=['nobody'], vals=[1])
create_items()
create_like(users=['nobody'], vals=[0])
create_users()
create_updates()
