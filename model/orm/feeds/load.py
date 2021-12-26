#!/usr/bin/env python3

import sqlalchemy as sqla

from model.orm import feeds as orm_feeds

def load_tags(
    q: sqla.sql.Select,
    user_id: int,
    tags_joined: bool = False,
) -> sqla.sql.Select:
    load_tags = load_tags_option(user_id, tags_joined)
    q = q.options(load_tags)

    return q

def load_tags_option(
    user_id: int,
    tags_joined: bool = False,
    load_option: sqla.orm.Load = None,
) -> sqla.orm.Load:
    if load_option is None:
        load_option = sqla.orm

    feed_tags = orm_feeds.Feed.tags.and_(
        orm_feeds.Tag.UserID == user_id,
    )

    if tags_joined:
        load_tags = load_option.contains_eager(feed_tags)
    else:
        load_tags = load_option.selectinload(feed_tags)

    return load_tags

