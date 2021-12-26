#!/usr/bin/env python3

import sqlalchemy as sqla

from model.orm import items as orm_items
from model.orm import users as orm_users

def order_date(
    q: sqla.sql.Select,
    desc: bool = True,
) -> sqla.sql.Select:
    item_published = orm_items.Item.Published
    if desc:
        item_published = sqla.desc(item_published)

    q = q.order_by(item_published)

    return q

def order_magic(
    q: sqla.sql.Select,
    user: orm_users.User,
    desc: bool = True,
) -> sqla.sql.Select:
    item_magic = orm_items.Item.magic.and_(
        orm_items.Magic.UserID == user.UserID,
    )

    q = q.join(item_magic, isouter=True)

    magic_score = orm_items.Magic.Score
    if desc:
        magic_score = sqla.desc(magic_score)

    q = q.order_by(magic_score)

    return q

