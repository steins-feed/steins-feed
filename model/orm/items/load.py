#!/usr/bin/env python3

import sqlalchemy as sqla

from model.orm import items as orm_items
from model.orm.feeds import load as feeds_load

def load_like(
    q: sqla.sql.Select,
    user_id: int,
    like_joined: bool = False,
) -> sqla.sql.Select:
    item_likes = orm_items.Item.likes.and_(
        orm_items.Like.UserID == user_id,
    )

    if like_joined:
        load_like = sqla.orm.contains_eager(item_likes)
    else:
        load_like = sqla.orm.selectinload(item_likes)

    q = q.options(load_like)

    return q

def load_magic(
    q: sqla.sql.Select,
    user_id: int,
    magic_joined: bool = False,
) -> sqla.sql.Select:
    item_magic = orm_items.Item.magic.and_(
        orm_items.Magic.UserID == user_id,
    )

    if magic_joined:
        load_magic = sqla.orm.contains_eager(item_magic)
    else:
        load_magic = sqla.orm.selectinload(item_magic)

    q = q.options(load_magic)

    return q

def load_tags(
    q: sqla.sql.Select,
    user_id: int,
    feed_joined: bool = False,
    tags_joined: bool = False,
) -> sqla.sql.Select:
    load_feed_tags = load_tags_option(user_id, feed_joined, tags_joined)
    q = q.options(load_feed_tags)

    return q

def load_tags_option(
    user_id: int,
    feed_joined: bool = False,
    tags_joined: bool = False,
    load_option: sqla.orm.Load = None,
) -> sqla.orm.Load:
    if load_option is None:
        load_option = sqla.orm

    assert feed_joined or not tags_joined

    item_feed = orm_items.Item.feed

    if feed_joined:
        load_feed = load_option.contains_eager(item_feed)
    else:
        load_feed = load_option.selectinload(item_feed)

    load_feed_tags = feeds_load.load_tags_option(user_id, tags_joined, load_feed)

    return load_feed_tags

