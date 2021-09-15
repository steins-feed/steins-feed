#!/usr/bin/env python3

import sqlalchemy.orm as sqla_orm

from .. import get_table
from .. import Base

class User(Base):
    __table__ = get_table("Users")

    roles = sqla_orm.relationship(
        "Role",
        secondary=get_table("Users2Roles"),
        back_populates="users",
    )

class Role(Base):
    __table__ = get_table("Roles")

    users = sqla_orm.relationship(
        "User",
        secondary=get_table("Users2Roles"),
        back_populates="roles",
    )
