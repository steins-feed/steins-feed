#!/usr/bin/env python3

import sqlalchemy as sqla
import typing

from log import time as log_time
import model
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users

@log_time.log_time(__name__)
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

@log_time.log_time(__name__)
def upsert_feed(feed_id, title, link, lang):
    feeds = model.get_table('Feeds')

    if feed_id:
        q = feeds.update().values(
                Title = title,
                Link = link,
                Language = lang.name
        ).where(feeds.c.FeedID == feed_id)
    else:
        q = feeds.insert().values(
                Title = title,
                Link = link,
                Language = lang.name
        )
        q = q.prefix_with("OR IGNORE", dialect='sqlite')
    with model.get_connection() as conn:
        conn.execute(q)

    if not feed_id:
        q = sqla.select([
                feeds.c.FeedID
        ]).where(sqla.and_(
                feeds.c.Title == title,
                feeds.c.Link == link,
                feeds.c.Language == lang.name
        ))
        with model.get_connection() as conn:
            res = conn.execute(q).fetchone()
        return res['FeedID']

@log_time.log_time(__name__)
def upsert_display(
    user: orm_users.User,
    feed: orm_feeds.Feed,
    displayed: bool = True,
):
    with model.get_session() as session:
        user = session.get(
            orm_users.User,
            user.UserID,
        )
        feed = session.get(
            orm_feeds.Feed,
            feed.FeedID,
        )

        if displayed:
            feed.users.append(user)
        else:
            try:
                feed.users.remove(user)
            except ValueError:
                pass

        session.commit()

