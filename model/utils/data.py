#!/usr/bin/env python3

from sqlalchemy import sql

from .. import get_connection, get_table
from ..schema.feeds import Language

def all_langs_feeds():
    feeds = get_table('Feeds')

    q = sql.select([
        feeds.c.Language
    ]).distinct().order_by(
        sql.collate(feeds.c.Language, 'NOCASE')
    )
    with get_connection() as conn:
        res = conn.execute(q).fetchall()

    res = [Language[e['Language']] for e in res]
    return res
