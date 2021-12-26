#!/usr/bin/env python3

import sqlalchemy as sqla
import typing

from log import time as log_time
import model
from model.orm import feeds as orm_feeds
from model.schema import feeds as schema_feeds
from model.utils import all_langs_feeds

@log_time.log_time(__name__)
def feeds_lang(
    tag: orm_feeds.Tag,
    flag: bool = True,
) -> typing.Dict[schema_feeds.Language, typing.List[orm_feeds.Feed]]:
    res = dict()

    for lang_it in all_langs_feeds():
        q = sqla.select(
            orm_feeds.Feed
        ).where(
            orm_feeds.Feed.Language == lang_it.name,
        ).order_by(
            sqla.collate(orm_feeds.Feed.Title, 'NOCASE')
        )
        if flag:
            q = q.where(orm_feeds.Feed.tags.any(orm_feeds.Tag.TagID == tag.TagID))
        else:
            q = q.where(~orm_feeds.Feed.tags.any(orm_feeds.Tag.TagID == tag.TagID))

        with model.get_session() as session:
            res[lang_it] = [e[0] for e in session.execute(q)]

    return res

@log_time.log_time(__name__)
def delete_feeds_tagged(
    tag: orm_feeds.Tag,
    tagged: typing.List[orm_feeds.Feed],
):
    with model.get_session() as session:
        tag = session.get(
            orm_feeds.Tag,
            tag.TagID,
        )

        for feed_it in tagged:
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
def insert_feeds_untagged(
    tag: orm_feeds.Tag,
    tagged: typing.List[orm_feeds.Feed],
):
    with model.get_session() as session:
        tag = session.get(
            orm_feeds.Tag,
            tag.TagID,
        )

        for feed_it in tagged:
            feed_it = session.get(
                orm_feeds.Feed,
                feed_it.FeedID,
            )

            tag.feeds.append(feed_it)

        session.commit()

