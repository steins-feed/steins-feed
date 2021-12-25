#!/usr/bin/env python3

import datetime
import sqlalchemy as sqla
import typing

from log import time as log_time
import model
from model.orm import feeds as orm_feeds, items as orm_items, users as orm_users
from model.orm.feeds import filter as feeds_filter
from model.orm.items import filter as items_filter
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
    q = load_like(q, user_id)
    q = load_tags(q, user_id, feed_joined=True)

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
        q = order_magic(q, user_id)
        q = load_magic(q, user_id, magic_joined=True)
    else:
        q = q.order_by(sqla.desc(orm_items.Item.Published))

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

def order_magic(q, user_id, desc=True):
    item_magic = orm_items.Item.magic.and_(
        orm_items.Magic.UserID == user_id,
    )

    q = q.join(item_magic)

    magic_score = orm_items.Magic.Score
    if desc:
        magic_score = sqla.desc(magic_score)

    q = q.order_by(magic_score)
    return q

def load_like(q, user_id, like_joined=False):
    item_likes = orm_items.Item.likes.and_(
        orm_items.Like.UserID == user_id,
    )

    if like_joined:
        load_like = sqla.orm.contains_eager(item_likes)
    else:
        load_like = sqla.orm.selectinload(item_likes)

    q = q.options(load_like)
    return q

def load_tags(q, user_id, feed_joined=False, tags_joined=False):
    assert feed_joined or not tags_joined

    item_feed = orm_items.Item.feed

    if feed_joined:
        load_feed = sqla.orm.contains_eager(item_feed)
    else:
        load_feed = sqla.orm.selectinload(item_feed)

    feed_tags = orm_feeds.Feed.tags.and_(
        orm_feeds.Tag.UserID == user_id,
    )

    if tags_joined:
        load_feed_tags = load_feed.contains_eager(feed_tags)
    else:
        load_feed_tags = load_feed.selectinload(feed_tags)

    q = q.options(load_feed_tags)
    return q

def load_magic(q, user_id, magic_joined=False):
    item_magic = orm_items.Item.magic.and_(
        orm_items.Magic.UserID == user_id,
    )

    if magic_joined:
        load_magic = sqla.orm.contains_eager(item_magic)
    else:
        load_magic = sqla.orm.selectinload(item_magic)

    q = q.options(load_magic)
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

