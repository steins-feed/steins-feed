#!/usr/bin/env python3

from sqlalchemy import sql

from .. import get_connection, get_table

# Tag.
def upsert_tag(tag_id, user_id, name):
    tags = get_table('Tags')

    if tag_id:
        q = tags.update().values(
                UserID = user_id,
                Name = name
        ).where(tags.c.TagID == tag_id)
    else:
        q = tags.insert().values(
                UserID = user_id,
                Name = name
        )
        q = q.prefix_with("OR IGNORE", dialect='sqlite')
    with get_connection() as conn:
        conn.execute(q)

    if not tag_id:
        q = sql.select([
                tags.c.TagID
        ]).where(sql.and_(
                tags.c.UserID == user_id,
                tags.c.Name == name
        ))
        with get_connection() as conn:
            res = conn.execute(q).fetchone()

        return res['TagID']

def delete_tags(tag_ids):
    tags = get_table('Tags')

    q = tags.delete().where(
            tags.c.TagID.in_(tag_ids)
    )
    with get_connection() as conn:
        conn.execute(q)
