#!/usr/bin/env python3

from sqlalchemy import sql

from .. import engine, get_table
from ..schema import Like

def upsert_like(user_id, item_id, like_val):
    like = get_table('Like')

    q = sql.select([
            like
    ]).where(sql.and_(
            like.c.UserID == user_id,
            like.c.ItemID == item_id
    ))
    with engine.connect() as conn:
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

    with engine.connect() as conn:
        if score == like_val:
            conn.execute(q, score=Like.MEH.name)
        else:
            conn.execute(q, score=like_val.name)

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
    with engine.connect() as conn:
        conn.execute(q)

    if not feed_id:
        q = sql.select([
                feeds.c.FeedID
        ]).where(sql.and_(
                feeds.c.Title == title,
                feeds.c.Link == link,
                feeds.c.Language == lang.name
        ))
        with engine.connect() as conn:
            res = conn.execute(q).fetchone()
        return res['FeedID']

def upsert_display(user_id, feed_ids, disp):
    display = get_table('Display')

    if disp == 0:
        q = display.delete().where(sql.and_(
                display.c.UserID == user_id,
                display.c.FeedID.in_(feed_ids)
        ))
        with engine.connect() as conn:
            conn.execute(q)
    else:
        row_keys = ['UserID', 'FeedID']
        rows = [dict(zip(row_keys, (user_id, e))) for e in feed_ids]

        q = display.insert()
        q = q.prefix_with("OR IGNORE", dialect='sqlite')
        with engine.connect() as conn:
            conn.execute(q, rows)

def delete_feeds(feed_ids):
    feeds = get_table('Feeds')

    q = feeds.delete().where(feeds.c.FeedID.in_(feed_ids))
    with engine.connect() as conn:
        conn.execute(q)

def delete_tags_tagged(feed_id, tagged):
    tags2feeds = get_table('Tags2Feeds')

    q = tags2feeds.delete().where(sql.and_(
        tags2feeds.c.TagID.in_(tagged),
        tags2feeds.c.FeedID == feed_id
    ))
    with engine.connect() as conn:
        conn.execute(q)

def insert_tags_untagged(feed_id, untagged):
    tags2feeds = get_table('Tags2Feeds')

    row_keys = ("TagID", "FeedID")
    rows = [dict(zip(row_keys, (e, feed_id))) for e in untagged]

    q = tags2feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    with engine.connect() as conn:
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
    with engine.connect() as conn:
        conn.execute(q)

    if not tag_id:
        q = sql.select([
                tags.c.TagID
        ]).where(sql.and_(
                tags.c.UserID == user_id,
                tags.c.Name == name
        ))
        with engine.connect() as conn:
            res = conn.execute(q).fetchone()

        return res['TagID']

def delete_tags(tag_ids):
    tags = get_table('Tags')

    q = tags.delete().where(
            tags.c.TagID.in_(tag_ids)
    )
    with engine.connect() as conn:
        conn.execute(q)

def delete_feeds_tagged(tag_id, tagged):
    tags2feeds = get_table('Tags2Feeds')

    q = tags2feeds.delete().where(sql.and_(
        tags2feeds.c.TagID == tag_id,
        tags2feeds.c.FeedID.in_(tagged)
    ))
    with engine.connect() as conn:
        conn.execute(q)

def insert_feeds_untagged(tag_id, untagged):
    tags2feeds = get_table('Tags2Feeds')

    row_keys = ("TagID", "FeedID")
    rows = [dict(zip(row_keys, (tag_id, e))) for e in untagged]

    q = tags2feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    with engine.connect() as conn:
        conn.execute(q, rows)

# Magic.
def reset_magic(user_id=None, lang=None):
    feeds = get_table('Feeds')
    items = get_table('Items')
    magic = get_table('Magic')

    q = magic.delete()
    q_where = []
    if user_id:
        q_where.append(magic.c.UserID == user_id)
    if lang:
        if user_id:
            q_cte = sql.select([
                items.c.ItemID
            ]).select_from(
                items.join(feeds)
            ).where(
                feeds.c.Language == lang.name
            ).distinct()
        else:
            q_cte = sql.select([
                items.c.ItemID
            ]).select_from(
                items.join(feeds)
                     .join(magic)
            ).where(sql.and_(
                feeds.c.Language == lang.name,
                magic.c.UserID == user_id
            )).distinct()
        q_where.append(magic.c.ItemID.in_(q_cte))
    q = q.where(sql.and_(*q_where))
    with engine.connect() as conn:
        conn.execute(q)

def upsert_magic(user_id, items, scores):
    if len(items) != len(scores):
        raise IndexError()

    magic = get_table('Magic')

    rows = []
    for i in range(len(items)):
        rows.append({
            'UserID': user_id,
            'ItemID': items[i]['ItemID'],
            'Score': scores[i]
        })

    q = magic.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    with engine.connect() as conn:
        conn.execute(q, rows)
