#!/usr/bin/env python3

import sqlalchemy as sqla

from model.orm import feeds as orm_feeds

def order_title(
    q: sqla.sql.Select,
) -> sqla.sql.Select:
    q = q.order_by(
        sqla.collate(orm_feeds.Feed.Title, "NOCASE"),
    )

    return q

