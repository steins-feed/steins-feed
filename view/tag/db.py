#!/usr/bin/env python3

import sqlalchemy as sqla

from log import time as log_time
import model
from model.orm import feeds as orm_feeds
from model.schema import feeds as schema_feeds
from model.utils import all_langs_feeds

@log_time.log_time(__name__)
def feeds_lang(tag_id, flag=True):
    res = dict()

    for lang_it in all_langs_feeds():
        lang_it = schema_feeds.Language(lang_it)

        q = sqla.select(
            orm_feeds.Feed
        ).where(
            orm_feeds.Feed.Language == lang_it.name,
        ).order_by(
            sqla.collate(orm_feeds.Feed.Title, 'NOCASE')
        )
        if flag:
            q = q.where(orm_feeds.Feed.tags.any(orm_feeds.Tag.TagID == tag_id))
        else:
            q = q.where(~orm_feeds.Feed.tags.any(orm_feeds.Tag.TagID == tag_id))

        with model.get_session() as session:
            res[lang_it] = [e[0] for e in session.execute(q)]

    return res

