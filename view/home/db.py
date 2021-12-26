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

@log_time.log_time(__name__)
def updated_items(
    user_id: int,
    langs: typing.List[schema_feeds.Language],
    tags: typing.List[str],
    start: datetime.datetime,
    finish: datetime.datetime,
    last: datetime.datetime = None,
    magic: bool = False,
    unscored: bool = False,
):
    q = sqla.select(orm_items.Item)
    q = items_filter.filter_display(q, user_id)
    q = items_filter.filter_dates(q, start, finish)
    q = items_filter.filter_dates(q, finish=last)
    if langs:
        q = feeds_filter.filter_languages(q, langs)
    if tags:
        q = feeds_filter.filter_tags(q, tags, user_id)
    q = deduplicate_items(q)
    q = items_load.load_like(q, user_id)
    q = items_load.load_tags(q, user_id, feed_joined=True)

    if unscored:
        q = q.join(orm_items.Item.magic.and_(
            orm_items.Magic.UserID == user_id,
        ), isouter=True)
        q = q.where(
            ~orm_items.Item.magic.any(
                orm_items.Magic.UserID == user_id
            )
        )
        q = q.options(
            sqla.orm.contains_eager(orm_items.Item.magic),
        )
    elif magic:
        q = items_order.order_magic(q, user_id)
        q = items_load.load_magic(q, user_id, magic_joined=True)
    else:
        q = items_order.order_date(q)

    with model.get_session() as session:
        return [e[0] for e in session.execute(q).unique()]

def deduplicate_items(q):
    q = q.group_by(
        orm_items.Item.Title,
        orm_items.Item.Published,
    )
    q = q.having(
        orm_feeds.Feed.Title == sqla.func.min(orm_feeds.Feed.Title),
    )
    return q

@log_time.log_time(__name__)
def unscored_items(
    user_id: int,
    lang: schema_feeds.Language,
    tags: typing.List[str],
    start: datetime.datetime,
    finish: datetime.datetime,
    last: datetime.datetime = None,
):
    return updated_items(user_id, [lang], tags, start, finish, last, unscored=True)

@log_time.log_time(__name__)
def upsert_like(
    user_id: int,
    item_id: int,
    like_val: schema_items.Like,
):
    like = model.get_table("Like")

    q = sqla.select(
        like,
    ).where(
        like.c.UserID == user_id,
        like.c.ItemID == item_id,
    )
    with model.get_connection() as conn:
        res = conn.execute(q).fetchone()

    if res:
        score = schema_items.Like[res["Score"]]
        q = like.update().values(
            Score=sqla.bindparam("score")
        ).where(
            like.c.UserID == user_id,
            like.c.ItemID == item_id,
        )
    else:
        score = schema_items.Like.MEH
        q = like.insert().values(
            UserID=user_id,
            ItemID=item_id,
            Score=sqla.bindparam("score"),
        )

    with model.get_connection() as conn:
        if score == like_val:
            conn.execute(q, score=schema_items.Like.MEH.name)
        else:
            conn.execute(q, score=like_val.name)

@log_time.log_time(__name__)
def upsert_magic(
    user_id: int,
    items: typing.List[orm_items.Item],
    scores: typing.List[float],
):
    assert len(items) == len(scores)

    magic = model.get_table("Magic")

    rows = []
    for i in range(len(items)):
        rows.append({
            "UserID": user_id,
            "ItemID": items[i].ItemID,
            "Score": scores[i]
        })

    q = magic.insert()
    q = q.prefix_with("OR IGNORE", dialect="sqlite")
    with model.get_connection() as conn:
        conn.execute(q, rows)

