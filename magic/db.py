#!/usr/bin/env python3

import sqlalchemy as sqla

import model
from model.schema import feeds as schema_feeds

def reset_magic(
    user_id: int = None,
    lang: schema_feeds.Language = None,
):
    """
    Resets magic.

    Args:
      user_id: User ID.
      lang: Language.
    """
    feeds = model.get_table('Feeds')
    items = model.get_table('Items')
    magic = model.get_table('Magic')

    q = magic.delete()

    if user_id:
        q = q.where(magic.c.UserID == user_id)

    if lang:
        if user_id:
            q_cte = sqla.select(
                items.c.ItemID,
            ).select_from(
                items.join(feeds)
                     .join(magic)
            ).where(
                feeds.c.Language == lang.name,
                magic.c.UserID == user_id,
            ).distinct()
        else:
            q_cte = sqla.select(
                items.c.ItemID,
            ).select_from(
                items.join(feeds)
            ).where(
                feeds.c.Language == lang.name,
            ).distinct()

        q = q.where(magic.c.ItemID.in_(q_cte))

    with model.get_connection() as conn:
        conn.execute(q)

