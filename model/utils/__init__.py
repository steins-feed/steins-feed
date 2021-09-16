#!/usr/bin/env python3

import sqlalchemy as sqla

from .. import get_session
from ..orm.feeds import Feed
from ..schema.feeds import Language

def all_langs_feeds():
    q = sqla.select(
        Feed.Language
    ).order_by(
        sqla.collate(Feed.Language, "NOCASE")
    ).distinct()

    with get_session() as session:
        return [Language[e["Language"]] for e in session.execute(q)]
