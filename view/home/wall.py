#!/usr/bin/env python3

import enum
import sqlalchemy as sqla

from model.orm import users as orm_users
from model.orm.items import load as items_load
from model.orm.items import order as items_order

class WallMode(enum.Enum):
    CLASSIC = "Classic"
    MAGIC = "Magic"
    SURPRISE = "Surprise"

def order_wall(
    q: sqla.sql.Select,
    wall_mode: WallMode,
    user: orm_users.User,
) -> sqla.sql.Select:
    if wall_mode == WallMode.MAGIC:
        q = items_order.order_magic(q, user)
        q = items_load.load_magic(q, user, magic_joined=True)
    else:
        q = items_order.order_date(q)

    return q

