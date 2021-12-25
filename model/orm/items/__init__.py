#!/usr/bin/env python3

import sqlalchemy as sqla

from model import get_table
from model import Base
from model.orm.feeds import Feed
from model.orm.users import User

t_like = get_table("Like")
t_magic = get_table("Magic")

class Item(Base):
    __table__ = get_table("Items")

    feed = sqla.orm.relationship(
        "Feed",
        back_populates="items",
    )
    likes = sqla.orm.relationship(
        "Like",
        back_populates="item",
    )
    magic = sqla.orm.relationship(
        "Magic",
        back_populates="item",
    )

Feed.items = sqla.orm.relationship(
    "Item",
    back_populates="feed",
)

class Like(Base):
    __table__ = t_like
    __mapper_args__ = {
        "primary_key": [t_like.c.UserID, t_like.c.ItemID],
    }

    user = sqla.orm.relationship(
        "User",
        back_populates="likes",
    )
    item = sqla.orm.relationship(
        "Item",
        back_populates="likes",
    )

User.likes = sqla.orm.relationship(
    "Like",
    back_populates="user",
)

class Magic(Base):
    __table__ = t_magic
    __mapper_args__ = {
        "primary_key": [t_magic.c.UserID, t_magic.c.ItemID],
    }

    user = sqla.orm.relationship(
        "User",
        back_populates="magic",
    )
    item = sqla.orm.relationship(
        "Item",
        back_populates="magic",
    )

User.magic = sqla.orm.relationship(
    "Magic",
    back_populates="user",
)
