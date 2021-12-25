#!/usr/bin/env python3

import datetime
import sqlalchemy as sqla

from model.orm import feeds as orm_feeds
from model.orm import items as orm_items
from model.orm import users as orm_users

def filter_display(
    q: sqla.sql.Select,
    user_id: int,
) -> sqla.sql.Select:
    item_feed = orm_items.Item.feed
    q = q.join(item_feed)

    feed_users = orm_feeds.Feed.users.and_(
        orm_users.User.UserID == user_id,
    )
    q = q.join(feed_users)

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

