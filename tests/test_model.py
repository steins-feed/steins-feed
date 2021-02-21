#!/usr/bin/env python3

from datetime import datetime
import glob
import os
from sqlalchemy import func, sql, Integer

from model import get_connection, get_table
from model import get_session, get_model
from model.feeds import read_feeds
from model.utils.recent import last_updated
from model.xml import read_xml, write_xml
from view import app
from view.auth import get_user_datastore

def test_user_datastore():
    session = get_session()
    User = get_model('Users')

    user_datastore = get_user_datastore()
    user = user_datastore.create_user(
            name="hansolo",
            password="obiwankenobi"
    )
    session.commit()

    new_user = session.query(User).filter(User.Name == user.Name).one()
    assert(new_user is user)

def test_xml_read():
    session = get_session()
    User = get_model('Users')
    Feed = get_model('Feeds')

    user_id = session.query(User).filter(User.Name == "hansolo").one().UserID
    for file_it in glob.glob(os.path.join("feeds.d", "*.xml")):
        with open(file_it, 'r') as f:
            read_xml(f, user_id, file_it[len("feeds.d") + 1:-len(".xml")])

    assert(session.query(Feed).count() > 0)

def test_xml_write():
    session = get_session()
    User = get_model('Users')
    Tag = get_model('Tags')

    user_id = session.query(User).filter(User.Name == "hansolo").one().UserID
    tags_name = [e.Name for e in session.query(Tag).filter(Tag.UserID == user_id)]
    for tag_name in tags_name:
        with open(os.path.join("feeds.d", tag_name + ".xml"), 'w') as f:
            write_xml(f, user_id, tag_name)

def test_feeds():
    conn = get_connection()
    items = get_table('Items')
    read_feeds("The Atlantic")

    q = sql.select([func.count()]).select_from(items)
    res = conn.execute(q).fetchone()
    assert(res[0] > 0)

def test_last_updated():
    assert(isinstance(last_updated(), datetime))

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
