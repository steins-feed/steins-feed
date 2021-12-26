#!/usr/bin/env python3

import enum
import sqlalchemy as sqla

from model.orm.items import load as items_load
from model.orm.items import order as items_order

class WallMode(enum.Enum):
    CLASSIC = "Classic"
    MAGIC = "Magic"
    SURPRISE = "Surprise"

def order_wall(
    q: sqla.sql.Select,
    wall_mode: WallMode,
    user_id: int,
) -> sqla.sql.Select:
    if wall_mode == WallMode.MAGIC:
        q = items_order.order_magic(q, user_id)
        q = items_load.load_magic(q, user_id, magic_joined=True)
    else:
        q = items_order.order_date(q)

    return q

