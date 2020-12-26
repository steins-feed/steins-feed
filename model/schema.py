#!/usr/bin/env python3

import enum
import sqlalchemy as sqla
from sqlalchemy import func, schema

from . import get_engine, get_metadata, get_table

def create_schema():
    create_schema_users()
    create_schema_roles()

    create_schema_feeds()
    create_schema_display()
    create_schema_tags()

    create_schema_items()
    create_schema_likes()
    create_schema_magic()

TINYTEXT = sqla.String(2**8 - 1)
TEXT = sqla.String(2**16 - 1)
MEDIUMTEXT = sqla.String(2**24 - 1)
LONGTEXT = sqla.String(2**32 - 1)

class Like(enum.Enum):
    UP = 1
    MEH = 0
    DOWN = -1

class Language(enum.Enum):
    ENGLISH = 'English'
    GERMAN = 'German'
    SWEDISH = 'Swedish'

def gen_fk(c):
    return sqla.ForeignKey(c, onupdate='CASCADE', ondelete='CASCADE')

#------------------------------------------------------------------------------

def create_schema_users():
    users = sqla.Table("Users", get_metadata(),
            sqla.Column("UserID", sqla.Integer, primary_key=True),
            sqla.Column("Name", TINYTEXT, nullable=False, unique=True),
            sqla.Column("Password", TINYTEXT, nullable=False),
            sqla.Column("Email", TINYTEXT),
            sqla.Column("Active", sqla.Boolean)
    )
    users.create(get_engine(), checkfirst=True)

def create_schema_roles():
    roles = sqla.Table("Roles", get_metadata(),
            sqla.Column("RoleID", sqla.Integer, primary_key=True),
            sqla.Column("Name", TINYTEXT, nullable=False, unique=True),
            sqla.Column("Description", TEXT)
    )
    roles.create(get_engine(), checkfirst=True)

    users = get_table('Users')
    users2roles = sqla.Table("Users2Roles", get_metadata(),
            sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
            sqla.Column("RoleID", sqla.Integer, gen_fk(roles.c.RoleID), nullable=False),
            schema.UniqueConstraint('UserID', 'RoleID')
    )
    users2roles.create(get_engine(), checkfirst=True)

#------------------------------------------------------------------------------

def create_schema_feeds():
    feeds = sqla.Table("Feeds", get_metadata(),
            sqla.Column("FeedID", sqla.Integer, primary_key=True),
            sqla.Column("Title", TEXT, nullable=False, unique=True),
            sqla.Column("Link", TEXT, nullable=False, unique=True),
            sqla.Column("Language", sqla.Enum(Language)),
            sqla.Column("Added", sqla.DateTime, default=func.now()),
            sqla.Column("Updated", sqla.DateTime)
    )
    feeds.create(get_engine(), checkfirst=True)

def create_schema_display():
    users = get_table('Users')
    feeds = get_table('Feeds')
    display = sqla.Table("Display", get_metadata(),
            sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
            sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
            schema.UniqueConstraint('UserID', 'FeedID')
    )
    display.create(get_engine(), checkfirst=True)

def create_schema_tags():
    users = get_table('Users')
    tags = sqla.Table("Tags", get_metadata(),
            sqla.Column("TagID", sqla.Integer, primary_key=True),
            sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
            sqla.Column("Name", TINYTEXT, nullable=False),
            schema.UniqueConstraint('UserID', 'Name')
    )
    tags.create(get_engine(), checkfirst=True)

    feeds = get_table('Feeds')
    tags2feeds = sqla.Table("Tags2Feeds", get_metadata(),
            sqla.Column("TagID", sqla.Integer, gen_fk(tags.c.TagID), nullable=False),
            sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
            schema.UniqueConstraint('TagID', 'FeedID')
    )
    tags2feeds.create(get_engine(), checkfirst=True)

#------------------------------------------------------------------------------

def create_schema_items():
    feeds = get_table('Feeds')
    items = sqla.Table("Items", get_metadata(),
            sqla.Column("ItemID", sqla.Integer, primary_key=True),
            sqla.Column("Title", TEXT, nullable=False),
            sqla.Column("Link", TEXT, nullable=False),
            sqla.Column("Published", sqla.DateTime, nullable=False),
            sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
            sqla.Column("Summary", MEDIUMTEXT),
            schema.UniqueConstraint('Title', 'Published', 'FeedID')
    )
    items.create(get_engine(), checkfirst=True)

def create_schema_likes():
    users = get_table('Users')
    items = get_table('Items')
    likes = sqla.Table("Like", get_metadata(),
            sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
            sqla.Column("ItemID", sqla.Integer, gen_fk(items.c.ItemID), nullable=False),
            sqla.Column("Score", sqla.Enum(Like), nullable=False),
            sqla.Column("Added", sqla.DateTime, default=func.now()),
            sqla.Column("Updated", sqla.DateTime, default=func.now()),
            schema.UniqueConstraint('UserID', 'ItemID')
    )
    likes.create(get_engine(), checkfirst=True)

def create_schema_magic():
    users = get_table('Users')
    items = get_table('Items')
    magic = sqla.Table("Magic", get_metadata(),
            sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
            sqla.Column("ItemID", sqla.Integer, gen_fk(items.c.ItemID), nullable=False),
            sqla.Column("Score", sqla.Float, nullable=False),
            sqla.Column("Added", sqla.DateTime, default=func.now()),
            sqla.Column("Updated", sqla.DateTime, default=func.now()),
            schema.UniqueConstraint('UserID', 'ItemID'),
            schema.CheckConstraint(
                    "Score BETWEEN {} AND {}".format(Like.DOWN.value, Like.UP.value)
            )
    )
    magic.create(get_engine(), checkfirst=True)
