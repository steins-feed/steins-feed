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
from model.utils import all_langs_feeds

@log_time.log_time(__name__)
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

@log_time.log_time(__name__)
def feeds_lang_disp(
    user: orm_users.User,
    flag: bool = True,
) -> typing.List[orm_feeds.Feed]:
    res = dict()

    for lang_it in all_langs_feeds():
        q = sqla.select(orm_feeds.Feed)
        q = feeds_filter.filter_languages(q, [lang_it])
        q = feeds_order.order_title(q)

        q_where = orm_feeds.Feed.users.any(
            orm_users.User.UserID == user.UserID,
        )

        if not flag:
            q_where = ~q_where

        q = q.where(q_where)

        with model.get_session() as session:
            res[lang_it] = [e[0] for e in session.execute(q)]

    return res

