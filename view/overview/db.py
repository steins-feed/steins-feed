#!/usr/bin/env python3

import sqlalchemy as sqla
import typing

from log import time as log_time
import model
from model.orm import items as orm_items
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users
from model.orm.feeds import filter as feeds_filter
from model.orm.feeds import order as feeds_order
from model.orm.items import filter as items_filter
from model.orm.items import load as items_load
from model.orm.items import order as items_order
from model.schema import feeds as schema_feeds
from model.schema import items as schema_items

@log_time.log_time(__name__)
def all_langs():
    q = sqla.select(
        orm_feeds.Feed.Language,
    ).order_by(
        sqla.collate(orm_feeds.Feed.Language, "NOCASE"),
    ).distinct()

    with model.get_session() as session:
        return [schema_feeds.Language[e["Language"]] for e in session.execute(q)]

@log_time.log_time(__name__)
def all_likes(
    user: orm_users.User,
    lang: schema_feeds.Language,
    score: schema_items.Like = schema_items.Like.UP,
) -> typing.Dict[schema_feeds.Language, typing.List[orm_items.Item]]:
    q = sqla.select(orm_items.Item)
    q = items_filter.filter_lang(q, lang)
    q = items_filter.filter_like(q, score, user)
    q = items_order.order_date(q)
    q = items_load.load_feed(q, feed_joined=True)

    with model.get_session() as session:
        return [e[0] for e in session.execute(q)]

