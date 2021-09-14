#!/usr/bin/env python3

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from .. import get_table
from .. import Base

t_tags2feeds = get_table("Tags2Feeds")

class Tag(Base):
    __table__ = get_table("Tags")

    feeds = sqla_orm.relationship(
        "TaggedFeed",
        secondary=t_tags2feeds,
        back_populates="tags",
    )

class TaggedFeed(Base):
    __table__ = get_table("Feeds")

    tags = sqla_orm.relationship(
        "Tag",
        secondary=t_tags2feeds,
        back_populates="feeds",
    )
