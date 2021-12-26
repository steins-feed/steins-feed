#!/usr/bin/env python3

import sqlalchemy as sqla
import typing

import model
from model.orm import items as orm_items
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users
from model.orm.items import filter as items_filter
from model.orm.items import load as items_load
from model.orm.items import order as items_order
from model.schema import feeds as schema_feeds
from model.schema import items as schema_items
from model.utils import all_langs_feeds

def likes_lang(
    user: orm_users.User,
    score: schema_items.Like = schema_items.Like.UP,
) -> typing.Dict[schema_feeds.Language, typing.List[orm_items.Item]]:
    q = sqla.select(orm_items.Item)
    q = items_filter.filter_lang(q, sqla.bindparam("lang"))
    q = items_filter.filter_like(q, score, user)
    q = items_order.order_date(q)
    q = items_load.load_feed(q, feed_joined=True)

    res = dict()
    with model.get_session() as session:
        for lang_it in all_langs_feeds():
            res[lang_it] = [
                e[0] for e in session.execute(q, {"lang": lang_it.name})
            ]

    return res

