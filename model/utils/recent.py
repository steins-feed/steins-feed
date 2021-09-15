#!/usr/bin/env python3

from datetime import datetime

import sqlalchemy as sqla

from .. import get_session
from ..orm.feeds import Feed
from ..orm.items import Like
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
    try:
        q = sqla.select([sqla.func.max(Like.Updated)])
        if user_id:
            q = q.where(Like.UserID == user_id)

        with get_session() as session:
            res = session.execute(q).fetchone()[0]

        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.utcfromtimestamp(0)

    return res
