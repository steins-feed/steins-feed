#!/usr/bin/env python3

import enum
import sqlalchemy as sqla

from . import TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT
from . import gen_fk

from .. import get_connection, get_table

class Language(enum.Enum):
    ENGLISH = 'English'
    GERMAN = 'German'
    SWEDISH = 'Swedish'

def create_schema():
    metadata = sqla.MetaData()

    users = get_table("Users")

    # Feeds.
    feeds = sqla.Table(
        "Feeds",
        metadata,
        sqla.Column("FeedID", sqla.Integer, primary_key=True),
        sqla.Column("Title", TEXT, nullable=False, unique=True),
        sqla.Column("Link", TEXT, nullable=False, unique=True),
        sqla.Column("Language", sqla.Enum(Language)),
        sqla.Column("Added", sqla.DateTime, server_default=sqla.func.now()),
        sqla.Column("Updated", sqla.DateTime),
    )

    with get_connection() as conn:
        feeds.create(conn, checkfirst=True)

    # Display.
    display = sqla.Table(
        "Display",
        metadata,
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
        sqla.UniqueConstraint("UserID", "FeedID"),
    )

    with get_connection() as conn:
        display.create(conn, checkfirst=True)

    # Tags.
    tags = sqla.Table(
        "Tags",
        metadata,
        sqla.Column("TagID", sqla.Integer, primary_key=True),
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("Name", TINYTEXT, nullable=False),
        sqla.UniqueConstraint("UserID", "Name"),
    )

    with get_connection() as conn:
        tags.create(conn, checkfirst=True)

    # Many-to-many relationship.
    tags2feeds = sqla.Table(
        "Tags2Feeds",
        metadata,
        sqla.Column("TagID", sqla.Integer, gen_fk(tags.c.TagID), nullable=False),
        sqla.Column("FeedID", sqla.Integer, gen_fk(feeds.c.FeedID), nullable=False),
        sqla.UniqueConstraint("TagID", "FeedID"),
    )

    with get_connection() as conn:
        tags2feeds.create(conn, checkfirst=True)
