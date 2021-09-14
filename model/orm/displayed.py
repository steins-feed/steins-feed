#!/usr/bin/env python3

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from .. import get_table
from .. import Base

t_display = get_table("Display")

class UserDisplay(Base):
    __table__ = get_table("Users")

    feeds = sqla_orm.relationship(
        "DisplayedFeed",
        secondary=t_display,
        back_populates="users",
    )

class DisplayedFeed(Base):
    __table__ = get_table("Feeds")

    users = sqla_orm.relationship(
        "UserDisplay",
        secondary=t_display,
        back_populates="feeds",
    )
