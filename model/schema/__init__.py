#!/usr/bin/env python3

import sqlalchemy as sqla

TINYTEXT = sqla.String(2**8 - 1)
TEXT = sqla.String(2**16 - 1)
MEDIUMTEXT = sqla.String(2**24 - 1)
LONGTEXT = sqla.String(2**32 - 1)

def gen_fk(c):
    return sqla.ForeignKey(c, onupdate='CASCADE', ondelete='CASCADE')

def create_schema():
    from . import users
    users.create_schema()

    from . import feeds
    feeds.create_schema()

    from . import items
    items.create_schema()
