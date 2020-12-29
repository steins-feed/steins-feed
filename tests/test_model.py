#!/usr/bin/env python3

from datetime import datetime
import glob
from sqlalchemy import func, sql, Integer

from model import get_connection, get_session, get_table
from model.feeds import read_feeds
from model.utils.recent import last_updated
from model.xml import read_xml, write_xml
from view import app
from view.auth import get_user_datastore

def test_xml_read():
    conn = get_connection()
    feeds = get_table('Feeds')

    for file_it in glob.glob("feeds.d/*.xml"):
        with open(file_it, 'r') as f:
            read_xml(f)

    q = sql.select([func.count()]).select_from(feeds)
    res = conn.execute(q).fetchone()
    assert(res[0] > 0)

def test_xml_write():
    with open("tests/feeds.xml", 'w') as f:
        write_xml(f)

def test_feeds():
    conn = get_connection()
    items = get_table('Items')
    read_feeds("The Atlantic")

    q = sql.select([func.count()]).select_from(items)
    res = conn.execute(q).fetchone()
    assert(res[0] > 0)

def test_last_updated():
    assert(isinstance(last_updated(), datetime))

def test_user_datastore():
    conn = get_connection()
    users = get_table('Users')

    session = get_session()
    user_datastore = get_user_datastore()
    user = user_datastore.create_user(
            name="hansolo",
            password="obiwankenobi"
    )
    session.commit()

    q = sql.select([func.count()]).select_from(users)
    res = conn.execute(q).fetchone()
    assert(res[0] > 0)

def test_display():
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')

    user_datastore = get_user_datastore()
    with app.app_context():
        user = user_datastore.find_user(name="hansolo")

    q = sql.select([
            sql.literal_column(str(user.id), type_=Integer).label('UserID'),
            feeds.c.FeedID
    ])
    ins = display.insert().from_select(['UserID', 'FeedID'], q)
    conn.execute(ins.prefix_with("OR IGNORE"))

    q = sql.select([
            func.count()
    ]).select_from(
            feeds.join(display)
    )
    res = conn.execute(q).fetchone()
    assert(res[0] > 0)

def test_tags():
    conn = get_connection()
    feeds = get_table('Feeds')
    tags = get_table('Tags')
    tags2feeds = get_table('Tags2Feeds')

    user_datastore = get_user_datastore()
    with app.app_context():
        user = user_datastore.find_user(name="hansolo")

    ins = tags.insert().values(UserID=user.id, Name="News")
    conn.execute(ins.prefix_with("OR IGNORE"))

    q = sql.select([
            tags.c.TagID,
            feeds.c.FeedID
    ]).where(
            feeds.c.Title == "The Atlantic"
    )
    ins = tags2feeds.insert().from_select([
            tags2feeds.c.TagID,
            tags2feeds.c.FeedID]
    , q)
    conn.execute(ins.prefix_with("OR IGNORE"))

    q = sql.select([
            func.count()
    ]).select_from(
            feeds.join(tags2feeds)
                 .join(tags)
    )
    res = conn.execute(q).fetchone()
    assert(res[0] > 0)
