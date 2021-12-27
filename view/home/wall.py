#!/usr/bin/env python3

import enum
import random
import sqlalchemy as sqla
import typing

from log import time as log_time
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
    elif wall_mode == WallMode.SURPRISE:
        q = items_order.order_date(q)
        q = items_load.load_magic(q, user)
    else:
        q = items_order.order_date(q)

    return q

@log_time.log_time(__name__)
def sample_wall(
    items: typing.List[orm_items.Item],
    wall_mode: WallMode,
) -> typing.List[orm_items.Item]:
    new_items = items

    if wall_mode == WallMode.RANDOM:
        new_items = choices(items, 10)
    elif wall_mode == WallMode.SURPRISE:
        w = [item_it.magic[0].Score for item_it in items]
        new_items = choices(items, 10, w)

    return new_items

def choices(
    items: typing.List[orm_items.Item],
    k: int,
    weights: typing.List[float] = None,
) -> typing.List[orm_items.Item]:
    n = len(items)
    if n <= k:
        return items

    keys = set()
    while len(keys) < k:
        new_keys = random.choices(
            range(n),
            weights = weights,
            k = k - len(keys),
        )
        keys |= set(new_keys)

    return [items[key_it] for key_it in sorted(keys)]

