#!/usr/bin/env python3

import enum
import sqlalchemy as sqla
from sqlalchemy import func, schema

from model import engine, get_table

TINYTEXT = sqla.String(2**8 - 1)
TEXT = sqla.String(2**16 - 1)
MEDIUMTEXT = sqla.String(2**24 - 1)
LONGTEXT = sqla.String(2**32 - 1)

class Like(enum.Enum):
    UP = 1
    MEH = 0
    DOWN = -1

def gen_fk(c):
    return sqla.ForeignKey(c, onupdate='CASCADE', ondelete='CASCADE')

def create_schema():
    from . import users
    users.create_schema()

    from . import feeds
    feeds.create_schema()

    create_schema_items()
    create_schema_likes()
    create_schema_magic()

#------------------------------------------------------------------------------

def create_schema_items():
    feeds = get_table('Feeds')
    items = sqla.Table("Items", sqla.MetaData(),
            sqla.Column("ItemID", sqla.Integer, primary_key=True),
            sqla.Column("Title", TEXT, nullable=False),
            sqla.Column("Link", TEXT, nullable=False),
            sqla.Column("Published", sqla.DateTime, nullable=False),
            sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
            sqla.Column("Summary", MEDIUMTEXT),
            schema.UniqueConstraint('Title', 'Published', 'FeedID')
    )
    items.create(engine, checkfirst=True)

def create_schema_likes():
    users = get_table('Users')
    items = get_table('Items')
    likes = sqla.Table("Like", sqla.MetaData(),
            sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
            sqla.Column("ItemID", sqla.Integer, gen_fk(items.c.ItemID), nullable=False),
            sqla.Column("Score", sqla.Enum(Like), nullable=False),
            sqla.Column("Added", sqla.DateTime, server_default=func.now()),
            sqla.Column("Updated", sqla.DateTime, server_default=func.now(), server_onupdate=func.now()),
            schema.UniqueConstraint('UserID', 'ItemID')
    )
    likes.create(engine, checkfirst=True)

def create_schema_magic():
    users = get_table('Users')
    items = get_table('Items')
    magic = sqla.Table("Magic", sqla.MetaData(),
            sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
            sqla.Column("ItemID", sqla.Integer, gen_fk(items.c.ItemID), nullable=False),
            sqla.Column("Score", sqla.Float, nullable=False),
            sqla.Column("Added", sqla.DateTime, server_default=func.now()),
            sqla.Column("Updated", sqla.DateTime, server_default=func.now(), server_onupdate=func.now()),
            schema.UniqueConstraint('UserID', 'ItemID'),
            schema.CheckConstraint(
                    "Score BETWEEN {} AND {}".format(Like.DOWN.value, Like.UP.value)
            )
    )
    magic.create(engine, checkfirst=True)
