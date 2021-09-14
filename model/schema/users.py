#!/usr/bin/env python3

import sqlalchemy as sqla

from . import TINYTEXT, TEXT, MEDIUMTEXT, LONGTEXT
from . import gen_fk

from .. import engine

def create_schema():
    metadata = sqla.MetaData()

    # Users.
    users = sqla.Table(
        "Users",
        metadata,
        sqla.Column("UserID", sqla.Integer, primary_key=True),
        sqla.Column("Name", TINYTEXT, nullable=False, unique=True),
        sqla.Column("Password", TINYTEXT, nullable=False),
        sqla.Column("Email", TINYTEXT, nullable=False, unique=True),
        sqla.Column("Active", sqla.Boolean, nullable=False),
        sqla.Column("fs_uniquifier", TINYTEXT, nullable=False, unique=True),
    )
    users.create(engine, checkfirst=True)

    # Roles.
    roles = sqla.Table(
        "Roles",
        metadata,
        sqla.Column("RoleID", sqla.Integer, primary_key=True),
        sqla.Column("Name", TINYTEXT, nullable=False, unique=True),
        sqla.Column("Description", TEXT),
    )
    roles.create(engine, checkfirst=True)

    # Many-to-many relationship.
    users2roles = sqla.Table(
        "Users2Roles",
        metadata,
        sqla.Column("UserID", sqla.Integer, gen_fk(users.c.UserID), nullable=False),
        sqla.Column("RoleID", sqla.Integer, gen_fk(roles.c.RoleID), nullable=False),
        sqla.UniqueConstraint('UserID', 'RoleID'),
    )
    users2roles.create(engine, checkfirst=True)
