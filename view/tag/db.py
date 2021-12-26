#!/usr/bin/env python3

import sqlalchemy as sqla
import typing

from log import time as log_time
import model
from model.orm import feeds as orm_feeds
from model.orm import users as orm_users
from model.schema import feeds as schema_feeds

from ..overview import db as overview_db

@log_time.log_time(__name__)
def insert_tag(
    user: orm_users.User,
    name: str,
) -> orm_feeds.Tag:
    with model.get_session() as session:
        tag = orm_feeds.Tag(
            UserID = user.UserID,
            Name = name,
        )
        session.add(tag)

        session.commit()
        session.refresh(tag)

    return tag

@log_time.log_time(__name__)
def delete_tags(
    *tags: orm_feeds.Tag,
):
    with model.get_session() as session:
        for tag_it in tags:
            session.delete(tag_it)

        session.commit()

@log_time.log_time(__name__)
def all_feeds(
    langs: typing.List[schema_feeds.Language] = None,
    tags: typing.List[orm_feeds.Tag] = None,
    flag: bool = True,
) -> typing.Dict[schema_feeds.Language, typing.List[orm_feeds.Feed]]:
    q = sqla.select(
        orm_feeds.Feed,
    ).order_by(
        sqla.collate(orm_feeds.Feed.Title, "NOCASE"),
    )

    if langs:
        q = q.where(
            orm_feeds.Feed.Language.in_(
                [lang_it.name for lang_it in langs]
            )
        )

    if tags:
        q_where = orm_feeds.Feed.tags.any(
            orm_feeds.Tag.TagID.in_(
                [tag_it.TagID for tag_it in tags]
            ),
        )

        if not flag:
            q_where = ~q_where

        q = q.where(q_where)

    with model.get_session() as session:
        return [e[0] for e in session.execute(q)]

@log_time.log_time(__name__)
def untag_feeds(
    tag: orm_feeds.Tag,
    *feeds: orm_feeds.Feed,
):
    with model.get_session() as session:
        tag = session.get(
            orm_feeds.Tag,
            tag.TagID,
        )

        for feed_it in feeds:
            feed_it = session.get(
                orm_feeds.Feed,
                feed_it.FeedID,
            )

            try:
                tag.feeds.remove(feed_it)
            except ValueError:
                pass

        session.commit()

@log_time.log_time(__name__)
def tag_feeds(
    tag: orm_feeds.Tag,
    *feeds: orm_feeds.Feed,
):
    with model.get_session() as session:
        tag = session.get(
            orm_feeds.Tag,
            tag.TagID,
        )

        for feed_it in feeds:
            feed_it = session.get(
                orm_feeds.Feed,
                feed_it.FeedID,
            )

            tag.feeds.append(feed_it)

        session.commit()

