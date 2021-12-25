#!/usr/bin/env python3

import sqlalchemy as sqla

import model
from model.schema import items as schema_items

def upsert_like(user_id, item_id, like_val):
    like = model.get_table('Like')

    q = sqla.select([
            like
    ]).where(sqla.and_(
            like.c.UserID == user_id,
            like.c.ItemID == item_id
    ))
    with model.get_connection() as conn:
        res = conn.execute(q).fetchone()

    if res:
        score = schema_items.Like[res['Score']]
        q = like.update().values(
               Score=sqla.bindparam("score")
        ).where(sqla.and_(
               like.c.UserID == user_id,
               like.c.ItemID == item_id
        ))
    else:
        score = schema_items.Like.MEH
        q = like.insert().values(
                UserID=user_id,
                ItemID=item_id,
                Score=sqla.bindparam("score")
        )

    with model.get_connection() as conn:
        if score == like_val:
            conn.execute(q, score=schema_items.Like.MEH.name)
        else:
            conn.execute(q, score=like_val.name)
