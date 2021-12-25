#!/usr/bin/env python3

import datetime
import sqlalchemy as sqla

import model
from model.orm import feeds as orm_feeds, items as orm_items, users as orm_users
from model.schema import feeds as schema_feeds

def last_updated(user_id: int=None) -> datetime.datetime:
    try:
        q = sqla.select(sqla.func.min(orm_feeds.Feed.Updated))
        if user_id:
            q = q.where(orm_feeds.Feed.users.any(orm_users.User.UserID == user_id))

        with model.get_session() as session:
            res = session.execute(q).fetchone()[0]

        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.datetime.utcfromtimestamp(0)

    return res

def last_liked(
    user_id: int = None,
    lang: schema_feeds.Language = None,
) -> datetime.datetime:
    try:
        q = sqla.select([sqla.func.max(orm_items.Like.Updated)])

        if user_id:
            q = q.where(orm_items.Like.UserID == user_id)

        if lang:
            q = q.join(orm_items.Like.item).join(orm_items.Item.feed)
            q = q.where(orm_feeds.Feed.Language == lang.name)

        with model.get_session() as session:
            res = session.execute(q).fetchone()[0]

        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.datetime.utcfromtimestamp(0)

    return res
