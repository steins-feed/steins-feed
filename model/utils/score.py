#!/usr/bin/env python3

from sqlalchemy import sql

from .. import get_connection, get_table
from ..schema import Like

def upsert_like(user_id, item_id, like_val):
    conn = get_connection()
    like = get_table('Like')

    q = sql.select([
            like]
    ).where(sql.and_(
            like.c.UserID == user_id,
            like.c.ItemID == item_id
    ))
    res = conn.execute(q).fetchone()

    if res:
        score = res['Score']
        q = like.update().values(
               Score=sql.bindparam("score")
        ).where(sql.and_(
               like.c.UserID == user_id,
               like.c.ItemID == item_id
        ))
    else:
        score = Like.MEH.name
        q = like.insert().values(
                UserID=user_id,
                ItemID=item_id,
                Score=sql.bindparam("score")
        )

    if score == like_val.name:
        conn.execute(q, score=Like.MEH.name)
    else:
        conn.execute(q, score=like_val.name)

def reset_magic(user_id=None):
    conn = get_connection()
    magic = get_table('Magic')

    q = magic.delete()
    if user_id:
        q = q.where(magic.c.UserID == user_id)
    conn.execute(q)
