#!/usr/bin/env python3

import datetime
import sqlalchemy as sqla
import typing

from log import time as log_time
import model
from model.orm import feeds as orm_feeds
from model.orm import items as orm_items
from model.orm import users as orm_users
from model.orm.feeds import filter as feeds_filter
from model.orm.items import filter as items_filter
from model.orm.items import load as items_load
from model.orm.items import order as items_order
from model.schema import feeds as schema_feeds, items as schema_items

from . import wall

@log_time.log_time(__name__)
def updated_items(
    user: orm_users.User,
    langs: typing.List[schema_feeds.Language],
    tags: typing.List[orm_feeds.Tag],
    start: datetime.datetime,
    finish: datetime.datetime,
    last: datetime.datetime = None,
    wall_mode: wall.WallMode = wall.WallMode.CLASSIC,
):
    q = sqla.select(orm_items.Item)
    q = items_filter.filter_display(q, user)
    q = items_filter.filter_dates(q, start, finish)
    q = items_filter.filter_dates(q, finish=last)
    if langs:
        q = feeds_filter.filter_languages(q, langs)
    if tags:
        q = feeds_filter.filter_tags(q, tags, user)
    q = items_filter.deduplicate_items(q)
    q = items_load.load_like(q, user)
    q = items_load.load_tags(q, user, feed_joined=True)
    q = wall.order_wall(q, wall_mode, user)

    with model.get_session() as session:
        res = [e[0] for e in session.execute(q).unique()]

    res = wall.sample_wall(res, wall_mode)

    return res

@log_time.log_time(__name__)
def unscored_items(
    user: orm_users.User,
    lang: schema_feeds.Language,
    tags: typing.List[orm_feeds.Tag],
    start: datetime.datetime,
    finish: datetime.datetime,
    last: datetime.datetime = None,
):
    q = sqla.select(orm_items.Item)
    q = items_filter.filter_display(q, user)
    q = items_filter.filter_dates(q, start, finish)
    q = items_filter.filter_dates(q, finish=last)
    q = feeds_filter.filter_languages(q, [lang])
    if tags:
        q = feeds_filter.filter_tags(q, tags, user)
    q = items_filter.filter_magic(q, user)

    with model.get_session() as session:
        return [e[0] for e in session.execute(q).unique()]

@log_time.log_time(__name__)
def upsert_like(
    user: orm_users.User,
    item: orm_items.Item,
    like_val: schema_items.Like,
):
    with model.get_session() as session:
        like = session.get(orm_items.Like, {
            "UserID": user.UserID,
            "ItemID": item.ItemID,
        })
        if like is None:
            like = orm_items.Like(
                UserID = user.UserID,
                ItemID = item.ItemID,
                Score = schema_items.Like.MEH.name,
            )
            session.add(like)

        if like.Score == like_val.name:
            like.Score = schema_items.Like.MEH.name
        else:
            like.Score = like_val.name

        session.commit()

@log_time.log_time(__name__)
def upsert_magic(
    user: orm_users.User,
    items: typing.List[orm_items.Item],
    scores: typing.List[float],
):
    assert len(items) == len(scores)

    magic = model.get_table("Magic")

    rows = []
    for i in range(len(items)):
        rows.append({
            "UserID": user.UserID,
            "ItemID": items[i].ItemID,
            "Score": scores[i]
        })

    q = magic.insert()
    q = q.prefix_with("OR IGNORE", dialect="sqlite")
    with model.get_connection() as conn:
        conn.execute(q, rows)

