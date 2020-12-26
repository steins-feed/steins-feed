#!/usr/bin/env python3

from sqlalchemy import func, sql

from model import get_connection, get_table

def last_updated():
    conn = get_connection()
    feeds = get_table('Feeds')

    try:
        q = sql.select([func.min(feeds.c.Updated)])
        res = conn.execute(q).fetchone()[0]
        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.utcfromtimestamp(0)

    return res

def last_liked(user_id=None):
    conn = get_connection()
    like = get_table('Like')

    try:
        q = sql.select([func.max(like.c.Updated)])
        if user_id:
            q = q.where(like.c.UserID == user_id)
        res = conn.execute(q).fetchone()[0]
        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.utcfromtimestamp(0)

    return res
