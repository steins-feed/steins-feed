#!/usr/bin/env python3

from datetime import datetime

import sqlalchemy as sqla

from .. import get_session
from ..orm.feeds import Feed
from ..orm.users import User

def last_updated(user_id=None):
    try:
        q = sqla.select(sqla.func.min(Feed.Updated))
        if user_id:
            q = q.where(Feed.users.any(User.UserID == user_id))

        with get_session() as session:
            res = session.execute(q).fetchone()[0]

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
