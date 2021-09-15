#!/usr/bin/env python3

import sqlalchemy as sqla

from .. import get_table
from .. import Base

t_like = get_table("Like")
t_magic = get_table("Magic")

class Item(Base):
    __table__ = get_table("Items")

    feed = sqla.orm.relationship("Feed")
    likes = sqla.orm.relationship("Like")
    magic = sqla.orm.relationship("Magic")

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
