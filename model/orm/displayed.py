#!/usr/bin/env python3

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from .. import get_table
from .. import Base

t_display = get_table("Display")

class User(Base):
    __table__ = get_table("Users")

    feeds = sqla_orm.relationship(
        "Feed",
        secondary=t_display,
        back_populates="users",
    )

class Feed(Base):
    __table__ = get_table("Feeds")

    users = sqla_orm.relationship(
        "User",
        secondary=t_display,
        back_populates="feeds",
    )
