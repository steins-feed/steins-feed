#!/usr/bin/env python3

from datetime import datetime
import glob
import os
from sqlalchemy import exc, orm, sql, Integer

from model import get_connection, get_table
from model import Base, get_session
from model.feeds import read_feeds
from model.utils import last_updated
from model.xml import read_xml, write_xml
from view.auth import get_user_datastore

def get_model(name):
    try:
        Model = globals()[name]
    except KeyError:
        Model = type(
            name,
            (Base, ),
            {'__table__': get_table(name)}
        )
        globals()[name] = Model
    return Model

def test_user_datastore():
    session = get_session()
    User = get_model('Users')

    try:
        user_datastore = get_user_datastore()
        user_datastore.create_user(
            name="hansolo",
            password="obiwankenobi",
            email="death.star@empire.org"
        )
        session.commit()
    except exc.IntegrityError:
        session.rollback()

    assert(session.query(User).filter(User.Name == "hansolo").count())

def test_xml_read():
    session = get_session()
    User = get_model('Users')
    Feed = get_model('Feeds')
    Tag = get_model('Tags')
    tags2feeds = get_table('Tags2Feeds')

    # Building a many-to-many relationship.
    Feed.tags = orm.relationship(
        Tag,
        secondary = tags2feeds,
        back_populates = 'feeds'
    )
    Tag.feeds = orm.relationship(
        Feed,
        secondary = tags2feeds,
        back_populates = 'tags'
    )

    user_id = session.query(User.UserID).filter(User.Name == "hansolo").scalar()
    for file_it in glob.glob(os.path.join("feeds.d", "*.xml")):
        tag_name = file_it[len("feeds.d") + 1:-len(".xml")]
        with open(file_it, 'r') as f:
            read_xml(f, user_id, tag_name)

        q = (session.query(Tag.feeds)
                    .filter(
                        Tag.UserID == user_id,
                        Tag.Name == tag_name
                    ).count())
        assert(q)

def test_xml_write():
    session = get_session()
    User = get_model('Users')
    Tag = get_model('Tags')

    user_id = session.query(User.UserID).filter(User.Name == "hansolo").scalar()
    tags_name = [e.Name for e in session.query(Tag).filter(Tag.UserID == user_id)]
    for tag_name in tags_name:
        file_path = os.path.join("feeds.d", tag_name + ".xml")
        with open(file_path, 'w') as f:
            write_xml(f, user_id, tag_name)

        assert(os.path.isfile(file_path))

def test_feeds():
    session = get_session()
    Feed = get_model('Feeds')
    Item = get_model('Items')

    read_feeds("The Atlantic")
    assert(session.query(Item).join(Feed).filter(Feed.Title.like("The Atlantic%")).count())

def test_last_updated():
    assert(isinstance(last_updated(), datetime))

def test_display():
    feeds = get_table('Feeds')
    display = get_table('Display')

    session = get_session()
    User = get_model('Users')
    Feed = get_model('Feeds')

    # Building a many-to-many relationship.
    Feed.users = orm.relationship(
        User,
        secondary = display,
        back_populates = 'feeds'
    )
    User.feeds = orm.relationship(
        Feed,
        secondary = display,
        back_populates = 'users'
    )

    user_id = session.query(User.UserID).filter(User.Name == "hansolo").scalar()
    display_count = session.query(User.feeds).filter(User.UserID == user_id).count

    if not display_count():
        q = sql.select([
                sql.literal_column(str(user_id), type_=Integer).label('UserID'),
                feeds.c.FeedID
        ])
        ins = display.insert().from_select(['UserID', 'FeedID'], q)
        with get_connection() as conn:
            conn.execute(ins.prefix_with("OR IGNORE"))

    assert(display_count())

def test_tags():
    feeds = get_table('Feeds')
    tags = get_table('Tags')
    tags2feeds = get_table('Tags2Feeds')

    session = get_session()
    User = get_model('Users')
    Feed = get_model('Feeds')
    Tag = get_model('Tags')

    # Building a many-to-many relationship.
    Feed.tags = orm.relationship(
        Tag,
        secondary = tags2feeds,
        back_populates = 'feeds'
    )
    Tag.feeds = orm.relationship(
        Feed,
        secondary = tags2feeds,
        back_populates = 'tags'
    )

    user_id = session.query(User.UserID).filter(User.Name == "hansolo").scalar()
    ins = tags.insert().values(UserID=user_id, Name="news")
    with get_connection() as conn:
        conn.execute(ins.prefix_with("OR IGNORE"))

    q = sql.select([
            tags.c.TagID,
            feeds.c.FeedID
    ]).where(sql.and_(
            feeds.c.Title == "The Atlantic",
            tags.c.Name == "news"
    ))
    ins = tags2feeds.insert().from_select([
            tags2feeds.c.TagID,
            tags2feeds.c.FeedID]
    , q)
    with get_connection() as conn:
        conn.execute(ins.prefix_with("OR IGNORE"))

    q = (session.query(Tag.feeds)
                .filter(
                    Tag.Name == "news",
                    Tag.UserID == user_id,
                    Tag.feeds.any(Feed.Title.like("The Atlantic%"))
                ).count())
    assert(q)
