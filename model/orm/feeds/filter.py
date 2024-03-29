#!/usr/bin/env python3

import sqlalchemy as sqla
import typing

from model.orm import feeds as orm_feeds
from model.orm import items as orm_items
from model.orm import users as orm_users
from model.schema import feeds as schema_feeds

def filter_display(
    q: sqla.sql.Select,
    user: orm_users.User,
) -> sqla.sql.Select:
    feed_users = orm_feeds.Feed.users.and_(
        orm_users.User.UserID == user.UserID,
    )
    q = q.join(feed_users)

    return q

def filter_languages(
    q: sqla.sql.Select,
    langs: typing.List[schema_feeds.Language],
) -> sqla.sql.Select:
    langs_name = [e.name for e in langs]
    q = q.where(orm_feeds.Feed.Language.in_(langs_name))

    return q

def filter_tags(
    q: sqla.sql.Select,
    tags: typing.List[orm_feeds.Tag],
    user: orm_users.User,
) -> sqla.sql.Select:
    feed_tags = orm_feeds.Feed.tags.and_(
        orm_feeds.Tag.UserID == user.UserID,
    )
    q = q.join(feed_tags)

    q = q.where(
        orm_feeds.Tag.TagID.in_(
            [tag_it.TagID for tag_it in tags]
        )
    )

    return q

