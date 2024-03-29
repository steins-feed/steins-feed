#!/usr/bin/env python3

import sqlalchemy as sqla
import typing

from log import time as log_time
import model
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users
from model.schema import feeds as schema_feeds

@log_time.log_time(__name__)
def all_tags(
    user: orm_users.User = None,
    feed: orm_feeds.Feed = None,
    flag: bool = True,
    display: bool = True,
) -> typing.List[orm_feeds.Tag]:
    q = sqla.select(
        orm_feeds.Tag,
    ).order_by(
        sqla.collate(orm_feeds.Tag.Name, "NOCASE"),
    )

    if user:
        q = q.where(orm_feeds.Tag.UserID == user.UserID)

    if feed:
        q_where = orm_feeds.Tag.feeds.any(
            orm_feeds.Feed.FeedID == feed.FeedID,
        )

        if not flag:
            q_where = ~q_where

        q = q.where(q_where)

    if display:
        q = q.join(
            orm_feeds.Tag.feeds
        ).join(
            orm_feeds.Feed.users.and_(
                orm_users.User.UserID == user.UserID,
            )
        ).distinct()

    with model.get_session() as session:
        return [e[0] for e in session.execute(q)]

@log_time.log_time(__name__)
def insert_feed(
    title: str,
    link: str,
    lang: schema_feeds.Language,
) -> orm_feeds.Feed:
    with model.get_session() as session:
        feed = orm_feeds.Feed(
            Title = title,
            Link = link,
            Language = lang.name,
        )
        session.add(feed)

        session.commit()
        session.refresh(feed)

    return feed

@log_time.log_time(__name__)
def update_feed(
    feed: orm_feeds.Feed,
    title: str,
    link: str,
    lang: schema_feeds.Language,
):
    with model.get_session() as session:
        feed = session.get(
            orm_feeds.Feed,
            feed.FeedID,
        )

        feed.Title = title
        feed.Link = link
        feed.Language = lang.name

        session.commit()

@log_time.log_time(__name__)
def delete_feeds(
    *feeds: orm_feeds.Feed,
):
    with model.get_session() as session:
        for feed_it in feeds:
            session.delete(feed_it)

        session.commit()

@log_time.log_time(__name__)
def upsert_display(
    user: orm_users.User,
    *feeds: orm_feeds.Feed,
    displayed: bool = True,
):
    with model.get_session() as session:
        user = session.get(
            orm_users.User,
            user.UserID,
        )

        for feed_it in feeds:
            feed_it = session.get(
                orm_feeds.Feed,
                feed_it.FeedID,
            )

            if displayed:
                feed_it.users.append(user)
            else:
                try:
                    feed_it.users.remove(user)
                except ValueError:
                    pass

        session.commit()

@log_time.log_time(__name__)
def detach_tags(
    feed: orm_feeds.Feed,
    *tags: orm_feeds.Tag,
):
    with model.get_session() as session:
        feed = session.get(
            orm_feeds.Feed,
            feed.FeedID,
        )

        for tag_it in tags:
            tag_it = session.get(
                orm_feeds.Tag,
                tag_it.TagID,
            )

            try:
                feed.tags.remove(tag_it)
            except ValueError:
                pass

        session.commit()

@log_time.log_time(__name__)
def attach_tags(
    feed: orm_feeds.Feed,
    *tags: orm_feeds.Tag,
):
    with model.get_session() as session:
        feed = session.get(
            orm_feeds.Feed,
            feed.FeedID,
        )

        for tag_it in tags:
            tag_it = session.get(
                orm_feeds.Tag,
                tag_it.TagID,
            )

            feed.tags.append(tag_it)

        session.commit()

