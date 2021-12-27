#!/usr/bin/env python3

import enum
import random
import sqlalchemy as sqla
import typing

from model.orm import items as orm_items
from model.orm import users as orm_users
from model.orm.items import load as items_load
from model.orm.items import order as items_order

class WallMode(enum.Enum):
    CLASSIC = "Classic"
    RANDOM = "Random"
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

def sample_wall(
    items: typing.List[orm_items.Item],
    wall_mode: WallMode,
) -> typing.List[orm_items.Item]:
    new_items = items

    if wall_mode == WallMode.RANDOM:
        k = random.choices(range(len(items)), k=10)
        k = sorted(k)
        new_items = [items[i] for i in k]

    return new_items

