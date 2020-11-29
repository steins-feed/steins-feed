#!/usr/bin/env python3

import enum
import os
import os.path as os_path

import sqlalchemy as sqla
import sqlalchemy.schema as sqla_schema

TINYTEXT = sqla.String(2**8 - 1)
TEXT = sqla.String(2**16 - 1)
MEDIUMTEXT = sqla.String(2**24 - 1)
LONGTEXT = sqla.String(2**32 - 1)

class LIKE(enum.Enum):
    LIKE = 1
    DISLIKE = -1

# Generate foreign-key constraint.
def gen_fk(c):
    return sqla.ForeignKey(c, on_update='CASCADE', on_delete='CASCADE')

db_path = "sqlite:///" + os_path.normpath(os_path.join(
        os_path.dirname(__file__),
        os.pardir,
        "steins.db"
))
engine = sqla.create_engine(db_path, echo=True)
metadata = sqla.MetaData()

# Users.
users = sqla.Table("Users", metadata,
        sqla.Column("UserID", sqla.Integer, primary_key=True),
        sqla.Column("Name", TINYTEXT, nullable=False, unique=True)
)

# Feeds.
feeds = sqla.Table("Feeds", metadata,
        sqla.Column("FeedID", sqla.Integer, primary_key=True),
        sqla.Column("Title", TEXT, nullable=False, unique=True),
        sqla.Column("Link", TEXT, nullable=False, unique=True),
        sqla.Column("Language", TINYTEXT),
)

# Items.
items = sqla.Table("Items", metadata,
        sqla.Column("ItemID", sqla.Integer, primary_key=True),
        sqla.Column("Title", TEXT, nullable=False),
        sqla.Column("Link", TEXT, nullable=False),
        sqla.Column("Published", sqla.DateTime, nullable=False),
        sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
        sqla.Column("Summary", MEDIUMTEXT),
        sqla_schema.UniqueConstraint('Title', 'Published', 'FeedID')
)

# Display feeds.
display = sqla.Table("Display", metadata,
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
        sqla_schema.UniqueConstraint('UserID', 'FeedID')
)

# Tags.
tags = sqla.Table("Tags", metadata,
        sqla.Column("TagID", sqla.Integer, primary_key=True),
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("Name", TINYTEXT, nullable=False),
        sqla_schema.UniqueConstraint('UserID', 'Name')
)
tags2feeds = sqla.Table("Tags2Feeds", metadata,
        sqla.Column("TagID", sqla.Integer, gen_fk(tags.c.TagID), nullable=False),
        sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
        sqla_schema.UniqueConstraint('TagID', 'FeedID')
)

# Like.
like = sqla.Table("Like", metadata,
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("ItemID", sqla.Integer, gen_fk(items.c.ItemID), nullable=False),
        sqla.Column("Score", sqla.Enum(LIKE), nullable=False),
        sqla_schema.UniqueConstraint('UserID', 'ItemID')
)

# Magic.
magic = sqla.Table("Magic", metadata,
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("ItemID", sqla.Integer, gen_fk(items.c.ItemID), nullable=False),
        sqla.Column("Score", sqla.Float, sqla_schema.CheckConstraint("Score <= 1 AND Score >= -1"), nullable=False),
        sqla_schema.UniqueConstraint('UserID', 'ItemID')
)

metadata.create_all(engine)
