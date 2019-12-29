#!/usr/bin/env python3

from steins_sql import create_feeds, create_display, create_items, create_like, create_users, create_updates

# Create tables.
create_feeds()
create_display()
create_items()
create_like()
create_users()
create_updates()
