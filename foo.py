#!/usr/bin/env python3

import glob
from sqlalchemy import sql, Integer

from model import get_connection, get_session, get_table
from model.feeds import read_feeds
from model.schema import create_schema
from model.xml import read_xml

create_schema()
for file_it in glob.glob("feeds.d/*.xml"):
    with open(file_it, 'r') as f:
        read_xml(f)
read_feeds("The Atlantic")

from view.auth import get_user_datastore

session = get_session()
user_datastore = get_user_datastore()
user = user_datastore.create_user(name="hansolo", password="obiwankenobi")
session.commit()

conn = get_connection()
feeds = get_table('Feeds')
display = get_table('Display')
q = sql.select([sql.literal_column(str(user.id), type_=Integer).label('UserID'), feeds.c.FeedID]).where(feeds.c.Title.like("%The Atlantic%"))
conn.execute(q)
ins = display.insert().from_select(['UserID', 'FeedID'], q)
conn.execute(ins)
