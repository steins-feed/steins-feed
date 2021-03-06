#!/usr/bin/env python3

from datetime import datetime
from sqlalchemy import func, sql

from model import get_connection, get_table

def last_updated():
    feeds = get_table('Feeds')

    try:
        q = sql.select([func.min(feeds.c.Updated)])
        with get_connection() as conn:
            res = conn.execute(q).fetchone()[0]

        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.utcfromtimestamp(0)

    return res

def last_liked(user_id=None):
    like = get_table('Like')

    try:
        q = sql.select([func.max(like.c.Updated)])
        if user_id:
            q = q.where(like.c.UserID == user_id)
        with get_connection() as conn:
            res = conn.execute(q).fetchone()[0]

        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.utcfromtimestamp(0)

    return res
