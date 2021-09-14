#!/usr/bin/env python3

import enum
import sqlalchemy as sqla

from . import TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT
from . import gen_fk

from .. import get_connection, get_table

class Like(enum.Enum):
    UP = 1
    MEH = 0
    DOWN = -1

def create_schema():
    metadata = sqla.MetaData()

    users = get_table("Users")
    feeds = get_table("Feeds")

    # Items.
    items = sqla.Table(
        "Items",
        metadata,
        sqla.Column("ItemID", sqla.Integer, primary_key=True),
        sqla.Column("Title", TEXT, nullable=False),
        sqla.Column("Link", TEXT, nullable=False),
        sqla.Column("Published", sqla.DateTime, nullable=False),
        sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
        sqla.Column("Summary", MEDIUMTEXT),
        sqla.UniqueConstraint("Title", "Published", "FeedID"),
    )

    with get_connection() as conn:
        items.create(conn, checkfirst=True)

    # Likes.
    likes = sqla.Table(
        "Like",
        metadata,
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("ItemID", sqla.Integer, gen_fk(items.c.ItemID), nullable=False),
        sqla.Column("Score", sqla.Enum(Like), nullable=False),
        sqla.Column("Added", sqla.DateTime, server_default=sqla.func.now()),
        sqla.Column("Updated", sqla.DateTime, server_default=sqla.func.now(), server_onupdate=sqla.func.now()),
        sqla.UniqueConstraint("UserID", "ItemID"),
    )

    with get_connection() as conn:
        likes.create(conn, checkfirst=True)

    # Magic.
    magic = sqla.Table(
        "Magic",
        metadata,
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("ItemID", sqla.Integer, gen_fk(items.c.ItemID), nullable=False),
        sqla.Column("Score", sqla.Float, nullable=False),
        sqla.Column("Added", sqla.DateTime, server_default=sqla.func.now()),
        sqla.Column("Updated", sqla.DateTime, server_default=sqla.func.now(), server_onupdate=sqla.func.now()),
        sqla.UniqueConstraint("UserID", "ItemID"),
        sqla.CheckConstraint(
            "Score BETWEEN {} AND {}".format(Like.DOWN.value, Like.UP.value)
        ),
    )

    with get_connection() as conn:
        magic.create(conn, checkfirst=True)
