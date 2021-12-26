#!/usr/bin/env python3

import sqlalchemy as sqla
import typing

import model
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users

def feed_tags(
    user: orm_users.User,
    feed: orm_feeds.Feed,
    flag: bool = True,
) -> typing.List[orm_feeds.Tag]:
    q = sqla.select(
        orm_feeds.Tag,
    ).where(
        orm_feeds.Tag.UserID == user.UserID,
    ).order_by(
        sqla.collate(orm_feeds.Tag.Name, "NOCASE"),
    )

    q_where = orm_feeds.Tag.feeds.any(
        orm_feeds.Feed.FeedID == feed.FeedID,
    )
    if not flag:
        q_where = ~q_where
    q = q.where(q_where)

    with model.get_session() as session:
        return [e[0] for e in session.execute(q)]

