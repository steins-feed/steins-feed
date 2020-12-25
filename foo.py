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

from view.auth import get_user_datastore

session = get_session()
user_datastore = get_user_datastore()
user = user_datastore.create_user(name="hansolo", password="obiwankenobi")
session.commit()

conn = get_connection()
feeds = get_table('Feeds')
display = get_table('Display')
tags = get_table('Tags')
tags2feeds = get_table('Tags2Feeds')

q = sql.select([sql.literal_column(str(user.id), type_=Integer).label('UserID'), feeds.c.FeedID]).where(feeds.c.Title.like("%The Atlantic%"))
conn.execute(q)
ins = display.insert().from_select(['UserID', 'FeedID'], q)
conn.execute(ins)

ins = tags.insert().values(UserID=user.id, Name="News")
conn.execute(ins)

q = sql.select([tags.c.TagID, feeds.c.FeedID]).where(feeds.c.Title == "The Atlantic")
ins = tags2feeds.insert().from_select([tags2feeds.c.TagID, tags2feeds.c.FeedID], q)
conn.execute(ins)

read_feeds("The Atlantic")
