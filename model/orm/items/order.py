#!/usr/bin/env python3

import sqlalchemy as sqla

from model.orm import items as orm_items

def order_magic(
    q: sqla.sql.Select,
    user_id: int,
    desc: bool = True,
):
    item_magic = orm_items.Item.magic.and_(
        orm_items.Magic.UserID == user_id,
    )

    q = q.join(item_magic, isouter=True)

    magic_score = orm_items.Magic.Score
    if desc:
        magic_score = sqla.desc(magic_score)

    q = q.order_by(magic_score)

    return q

