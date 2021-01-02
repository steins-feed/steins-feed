#!/usr/bin/env python3

from sqlalchemy import sql

from .. import get_connection, get_table
from ..schema import Like

def upsert_like(user_id, item_id, like_val):
    conn = get_connection()
    like = get_table('Like')

    q = sql.select([
            like
    ]).where(sql.and_(
            like.c.UserID == user_id,
            like.c.ItemID == item_id
    ))
    res = conn.execute(q).fetchone()

    if res:
        score = Like[res['Score']]
        q = like.update().values(
               Score=sql.bindparam("score")
        ).where(sql.and_(
               like.c.UserID == user_id,
               like.c.ItemID == item_id
        ))
    else:
        score = Like.MEH
        q = like.insert().values(
                UserID=user_id,
                ItemID=item_id,
                Score=sql.bindparam("score")
        )

    if score == like_val:
        conn.execute(q, score=Like.MEH.name)
    else:
        conn.execute(q, score=like_val.name)

# Feed.
def upsert_feed(feed_id, title, link, lang):
    conn = get_connection()
    feeds = get_table('Feeds')

    q = feeds.update().values(
            Title = title,
            Link = link,
            Language = lang
    ).where(
            feeds.c.FeedID == feed_id
    )
    conn.execute(q)

def upsert_display(user_id, feed_id, disp):
    conn = get_connection()
    display = get_table('Display')

    if disp == 0:
        q = display.delete().where(sql.and_(
                display.c.UserID == sql.bindparam("user_id"),
                display.c.FeedID == sql.bindparam("feed_id")
        ))
    else:
        q = display.insert().values(
                UserID = sql.bindparam("user_id"),
                FeedID = sql.bindparam("feed_id")
        )
        q = q.prefix_with("OR IGNORE", dialect='sqlite')
    conn.execute(q, user_id=user_id, feed_id=feed_id)

def delete_tags_tagged(feed_id, tagged):
    conn = get_connection()
    tags2feeds = get_table('Tags2Feeds')

    q = tags2feeds.delete().where(sql.and_(
        tags2feeds.c.TagID.in_(tagged),
        tags2feeds.c.FeedID == feed_id
    ))
    conn.execute(q)

def insert_tags_untagged(feed_id, untagged):
    conn = get_connection()
    tags2feeds = get_table('Tags2Feeds')

    row_keys = ("TagID", "FeedID")
    rows = [dict(zip(row_keys, (e, feed_id))) for e in untagged]

    q = tags2feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    conn.execute(q, rows)

# Tag.
def add_tags(user_id, names):
    conn = get_connection()
    tags = get_table('Tags')

    row_keys = ('UserID', 'Name')
    rows = [dict(zip(row_keys, (user_id, e))) for e in names]

    q = tags.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    conn.execute(q, rows)

def delete_tags(tag_ids):
    conn = get_connection()
    tags = get_table('Tags')

    q = tags.delete().where(
            tags.c.TagID.in_(tag_ids)
    )
    conn.execute(q)

def delete_feeds_tagged(tag_id, tagged):
    conn = get_connection()
    tags2feeds = get_table('Tags2Feeds')

    q = tags2feeds.delete().where(sql.and_(
        tags2feeds.c.TagID == tag_id,
        tags2feeds.c.FeedID.in_(tagged)
    ))
    conn.execute(q)

def insert_feeds_untagged(tag_id, untagged):
    conn = get_connection()
    tags2feeds = get_table('Tags2Feeds')

    row_keys = ("TagID", "FeedID")
    rows = [dict(zip(row_keys, (tag_id, e))) for e in untagged]

    q = tags2feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    conn.execute(q, rows)

# Magic.
def reset_magic(user_id=None):
    conn = get_connection()
    magic = get_table('Magic')

    q = magic.delete()
    if user_id:
        q = q.where(magic.c.UserID == user_id)
    conn.execute(q)
