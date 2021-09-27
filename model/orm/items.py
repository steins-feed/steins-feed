#!/usr/bin/env python3

import sqlalchemy as sqla

from .. import get_table
from .. import Base
from .feeds import Feed

t_like = get_table("Like")
t_magic = get_table("Magic")

class Item(Base):
    __table__ = get_table("Items")

    feed = sqla.orm.relationship(
        "Feed",
        back_populates="items",
    )
    likes = sqla.orm.relationship("Like")
    magic = sqla.orm.relationship("Magic")

Feed.items = sqla.orm.relationship(
    "Item",
    back_populates="feed",
)

class Like(Base):
    __table__ = t_like
    __mapper_args__ = {
        "primary_key": [t_like.c.UserID, t_like.c.ItemID],
    }

class Magic(Base):
    __table__ = t_magic
    __mapper_args__ = {
        "primary_key": [t_magic.c.UserID, t_magic.c.ItemID],
    }
