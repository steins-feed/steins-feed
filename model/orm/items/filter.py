#!/usr/bin/env python3

import datetime
import sqlalchemy as sqla

from model.orm import feeds as orm_feeds
from model.orm import items as orm_items
from model.orm import users as orm_users
from model.orm.feeds import filter as feeds_filter

def filter_display(
    q: sqla.sql.Select,
    user: orm_users.User,
) -> sqla.sql.Select:
    item_feed = orm_items.Item.feed
    q = q.join(item_feed)

    q = feeds_filter.filter_display(q, user)

    return q

def filter_dates(
    q: sqla.sql.Select,
    start: datetime.datetime = None,
    finish: datetime.datetime = None,
) -> sqla.sql.Select:
    if start:
        q = q.where(
            orm_items.Item.Published >= start,
        )

    if finish:
        q = q.where(
            orm_items.Item.Published < finish,
        )

    return q

def filter_magic(
    q: sqla.sql.Select,
    user: orm_users.User,
    unscored: bool = True,
) -> sqla.sql.Select:
    item_magic = orm_items.Item.magic.and_(
        orm_items.Magic.UserID == user.UserID,
    )

    q = q.join(item_magic, isouter=True)

    q_where = orm_items.Item.magic.any(
        orm_items.Magic.UserID == user.UserID
    )
    if unscored:
        q_where = ~q_where

    q = q.where(q_where)

    return q

def deduplicate_items(
    q: sqla.sql.Select,
) -> sqla.sql.Select:
    q = q.group_by(
        orm_items.Item.Title,
        orm_items.Item.Published,
    )
    q = q.having(
        orm_feeds.Feed.Title == sqla.func.min(orm_feeds.Feed.Title),
    )
    return q

