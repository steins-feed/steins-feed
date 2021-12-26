#!/usr/bin/env python3

import sqlalchemy as sqla

from model.orm import feeds as orm_feeds
from model.orm import users as orm_users

def load_tags(
    q: sqla.sql.Select,
    user: orm_users.User,
    tags_joined: bool = False,
) -> sqla.sql.Select:
    load_tags = load_tags_option(user, tags_joined)
    q = q.options(load_tags)

    return q

def load_tags_option(
    user: orm_users.User,
    tags_joined: bool = False,
    load_option: sqla.orm.Load = None,
) -> sqla.orm.Load:
    if load_option is None:
        load_option = sqla.orm

    feed_tags = orm_feeds.Feed.tags.and_(
        orm_feeds.Tag.UserID == user.UserID,
    )

    if tags_joined:
        load_tags = load_option.contains_eager(feed_tags)
    else:
        load_tags = load_option.selectinload(feed_tags)

    return load_tags

