#!/usr/bin/env python3

from sqlalchemy import sql

from .. import get_connection, get_table

# Feed.
def upsert_feed(feed_id, title, link, lang):
    feeds = get_table('Feeds')

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
    with get_connection() as conn:
        conn.execute(q)

    if not feed_id:
        q = sql.select([
                feeds.c.FeedID
        ]).where(sql.and_(
                feeds.c.Title == title,
                feeds.c.Link == link,
                feeds.c.Language == lang.name
        ))
        with get_connection() as conn:
            res = conn.execute(q).fetchone()
        return res['FeedID']

def upsert_display(user_id, feed_ids, disp):
    display = get_table('Display')

    if disp == 0:
        q = display.delete().where(sql.and_(
                display.c.UserID == user_id,
                display.c.FeedID.in_(feed_ids)
        ))
        with get_connection() as conn:
            conn.execute(q)
    else:
        row_keys = ['UserID', 'FeedID']
        rows = [dict(zip(row_keys, (user_id, e))) for e in feed_ids]

        q = display.insert()
        q = q.prefix_with("OR IGNORE", dialect='sqlite')
        with get_connection() as conn:
            conn.execute(q, rows)

def delete_feeds(feed_ids):
    feeds = get_table('Feeds')

    q = feeds.delete().where(feeds.c.FeedID.in_(feed_ids))
    with get_connection() as conn:
        conn.execute(q)

def delete_tags_tagged(feed_id, tagged):
    tags2feeds = get_table('Tags2Feeds')

    q = tags2feeds.delete().where(sql.and_(
        tags2feeds.c.TagID.in_(tagged),
        tags2feeds.c.FeedID == feed_id
    ))
    with get_connection() as conn:
        conn.execute(q)

def insert_tags_untagged(feed_id, untagged):
    tags2feeds = get_table('Tags2Feeds')

    row_keys = ("TagID", "FeedID")
    rows = [dict(zip(row_keys, (e, feed_id))) for e in untagged]

    q = tags2feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    with get_connection() as conn:
        conn.execute(q, rows)

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

def delete_feeds_tagged(tag_id, tagged):
    tags2feeds = get_table('Tags2Feeds')

    q = tags2feeds.delete().where(sql.and_(
        tags2feeds.c.TagID == tag_id,
        tags2feeds.c.FeedID.in_(tagged)
    ))
    with get_connection() as conn:
        conn.execute(q)

def insert_feeds_untagged(tag_id, untagged):
    tags2feeds = get_table('Tags2Feeds')

    row_keys = ("TagID", "FeedID")
    rows = [dict(zip(row_keys, (tag_id, e))) for e in untagged]

    q = tags2feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    with get_connection() as conn:
        conn.execute(q, rows)
