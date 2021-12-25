#!/usr/bin/env python3

import datetime
import sqlalchemy as sqla
import typing

import model
from model.orm import feeds as orm_feeds, items as orm_items, users as orm_users
from model.schema import items as schema_items

def updated_dates(
    user_id: int,
    keys: typing.List[str],
    last: datetime.datetime = None,
    limit: int = None,
):
    q = sqla.select(
        [sqla.extract(e.lower(), orm_items.Item.Published).label(e) for e in keys]
    ).join(
        orm_items.Item.feed
    ).join(
        orm_feeds.Feed.users
    )

    q = q.where(orm_users.User.UserID == user_id)
    if last:
        q = q.where(orm_items.Item.Published < last)

    q = q.order_by(*[sqla.desc(e) for e in keys])
    if limit:
        q = q.limit(limit)
    q = q.distinct()

    date_string, format_string = keys2strings(keys)
    tuple2datetime = lambda x: datetime.datetime.strptime(
            date_string.format(*x),
            format_string
    )

    with model.get_session() as session:
        return [tuple2datetime(e) for e in session.execute(q)]

def keys2strings(keys):
    date_string = "{}"
    format_string = "%Y"

    for key_it in keys[1:]:
        if key_it == "Month":
            date_string += "-{}"
            format_string += "-%m"
        elif key_it == "Week":
            date_string += "-{}"
            format_string += "-%W"
        elif key_it == "Day":
            date_string += "-{}"
            format_string += "-%d"

    if keys[-1] == "Month":
        date_string += "-1"
        format_string += "-%d"
    elif keys[-1] == "Week":
        date_string += "-1"
        format_string += "-%w"

    return date_string, format_string

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
            "ItemID": items[i]["ItemID"],
            "Score": scores[i]
        })

    q = magic.insert()
    q = q.prefix_with("OR IGNORE", dialect="sqlite")
    with model.get_connection() as conn:
        conn.execute(q, rows)

