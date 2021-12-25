#!/usr/bin/env python3

import datetime
import sqlalchemy as sqla
import typing

from log import time as log_time
import model
from model.orm import feeds as orm_feeds, items as orm_items, users as orm_users
from model.schema import feeds as schema_feeds, items as schema_items

@log_time.log_time(__name__)
def updated_dates(
    user_id: int,
    keys: typing.List[str],
    last: datetime.datetime = None,
    limit: int = None,
) -> typing.List[datetime.datetime]:
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

def keys2strings(keys: typing.List[str]) -> typing.Tuple[str, str]:
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

@log_time.log_time(__name__)
def updated_dates_(
    user_id: int,
    langs: typing.List[schema_feeds.Language],
    tags: typing.List[str],
    last: datetime.datetime = None,
):
    # Maximum datetime.
    q = sqla.select(
        sqla.func.max(orm_items.Item.Published),
    ).join(
        orm_items.Item.feed
    ).join(
        orm_feeds.Feed.users.and_(
            orm_users.User.UserID == user_id,
        )
    )

    q = filter_dates(q, last=last)
    q = filter_languages(q, langs)
    q = filter_tags(q, tags, user_id)
    q = q.order_by(sqla.desc(orm_items.Item.Published))

    with model.get_session() as session:
        dt_max = session.execute(q).fetchone()[0]

    # Minimum datetime.
    q = sqla.select(
        sqla.func.min(orm_items.Item.Published),
    ).join(
        orm_items.Item.feed
    ).join(
        orm_feeds.Feed.users.and_(
            orm_users.User.UserID == user_id,
        )
    )

    q = filter_languages(q, langs)
    q = filter_tags(q, tags, user_id)
    q = q.order_by(sqla.desc(orm_items.Item.Published))

    with model.get_session() as session:
        dt_min = session.execute(q).fetchone()[0]

    return dt_min, dt_max

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
    q = sqla.select(
        orm_items.Item,
    ).join(
        orm_items.Item.feed
    ).join(
        orm_feeds.Feed.users.and_(
            orm_users.User.UserID == user_id,
        )
    )

    q = filter_dates(q, start, finish, last)
    q = filter_languages(q, langs)
    q = filter_tags(q, tags, user_id)
    q = deduplicate_items(q)

    q = q.options(
        sqla.orm.joinedload(orm_items.Item.likes.and_(
            orm_items.Like.UserID == user_id,
        )),
        sqla.orm.contains_eager(orm_items.Item.feed)
                .selectinload(orm_feeds.Feed.tags.and_(
            orm_feeds.Tag.UserID == user_id,
        )),
    )

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
        q = q.join(orm_items.Item.magic.and_(
            orm_items.Magic.UserID == user_id,
        ))
        q = q.order_by(sqla.desc(orm_items.Magic.Score))
        q = q.options(
            sqla.orm.contains_eager(orm_items.Item.magic),
        )
    else:
        q = q.order_by(sqla.desc(orm_items.Item.Published))

    with model.get_session() as session:
        return [e[0] for e in session.execute(q).unique()]

def filter_dates(q, start=None, finish=None, last=None):
    if start:
        q = q.where(
            orm_items.Item.Published >= start,
        )

    if finish:
        q = q.where(
            orm_items.Item.Published < finish,
        )

    if last:
        q = q.where(
            orm_items.Item.Published < last,
        )

    return q

def filter_languages(q, langs):
    if langs:
        q = q.where(
            orm_feeds.Feed.Language.in_([schema_feeds.Language(e).name for e in langs]),
        )

    return q

def filter_tags(q, tags, user_id):
    if tags:
        q = q.join(
            orm_feeds.Feed.tags.and_(
                orm_feeds.Tag.UserID == user_id,
            )
        )
        q = q.where(
            orm_feeds.Tag.Name.in_(tags),
        )

    return q

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

