#!/usr/bin/env python3

import sqlalchemy as sqla

from .. import get_table
from .. import Base
from .users import User

t_display = get_table("Display")
t_tags2feeds = get_table("Tags2Feeds")

class Feed(Base):
    __table__ = get_table("Feeds")

    users = sqla.orm.relationship(
        "User",
        secondary=t_display,
        back_populates="feeds",
    )
    tags = sqla.orm.relationship(
        "Tag",
        secondary=t_tags2feeds,
        back_populates="feeds",
    )

User.feeds = sqla.orm.relationship(
    "Feed",
    secondary=t_display,
    back_populates="users",
)

class Tag(Base):
    __table__ = get_table("Tags")

    feeds = sqla.orm.relationship(
        "Feed",
        secondary=t_tags2feeds,
        back_populates="tags",
    )
