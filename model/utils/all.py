#!/usr/bin/env python3

from sqlalchemy import func, sql

from .. import get_connection, get_table
from ..schema.feeds import Language
from ..schema.items import Like

def updated_items(user_id, langs, tags, start, finish, last=None, magic=False, unscored=False):
    t_feeds = get_table('Feeds')
    t_display = get_table('Display')
    t_tags = get_table('Tags')
    t_tags2feeds = get_table('Tags2Feeds')
    t_items = get_table('Items')
    t_like = get_table('Like')
    t_magic = get_table('Magic')

    q = sql.select([
        t_items,
        t_feeds.c.Title.label("Feed"),
        t_feeds.c.Language,
        t_display.c.UserID,
    ]).select_from(t_items.join(t_feeds)
                          .join(t_display))

    q_where = [
        t_display.c.UserID == user_id,
        t_items.c.Published >= start,
        t_items.c.Published < finish,
    ]
    if last:
        q_where.append(t_items.c.Published < last)
    if langs:
        q_lang = [t_feeds.c.Language == Language(e).name for e in langs]
        q_where.append(sql.or_(*q_lang))
    q = q.where(sql.and_(*q_where))

    q = q.group_by(
        t_items.c.Title,
        t_items.c.Published,
    )
    q = q.having(t_feeds.c.Title == func.min(t_feeds.c.Title))
    t_items_displayed = q.cte()

    q_select = [
        t_items_displayed,
        func.coalesce(func.group_concat(t_tags.c.TagID), "").label("TagIDs"),
        func.coalesce(func.group_concat(t_tags.c.Name), "").label("TagNames"),
        func.coalesce(t_like.c.Score, 0).label("Like"),
    ]
    if magic:
        q_select.append(t_magic.c.Score)
    q = sql.select(q_select)

    q_from = t_items_displayed.outerjoin(
        t_tags2feeds.join(t_tags), sql.and_(
            t_items_displayed.c.FeedID == t_tags2feeds.c.FeedID,
            t_items_displayed.c.UserID == t_tags.c.UserID,
    )).outerjoin(
        t_like, sql.and_(
            t_items_displayed.c.ItemID == t_like.c.ItemID,
            t_items_displayed.c.UserID == t_like.c.UserID,
    ))
    if magic:
        q_from = q_from.outerjoin(
            t_magic, sql.and_(
                t_items_displayed.c.ItemID == t_magic.c.ItemID,
                t_items_displayed.c.UserID == t_magic.c.UserID,
        ))
    q = q.select_from(q_from)

    q_where = [t_items_displayed.c.UserID == user_id]
    if tags:
        q_tag = [t_tags.c.Name == e for e in tags]
        q_where.append(sql.or_(*q_tag))
    if unscored:
        q_where.append(t_magic.c.Score == None)
    q = q.where(sql.and_(*q_where))

    q = q.group_by(t_items_displayed.c.ItemID)
    if unscored:
        pass
    elif magic:
        q = q.order_by(sql.desc(t_magic.c.Score))
    else:
        q = q.order_by(sql.desc(t_items_displayed.c.Published))
    with get_connection() as conn:
        return conn.execute(q).fetchall()

def liked_languages(user_id):
    t_feeds = get_table('Feeds')
    t_items = get_table('Items')
    t_like = get_table('Like')

    q = sql.select([
        t_feeds.c.Language
    ]).select_from(
        t_items.join(t_feeds)
               .join(t_like)
    ).where(sql.and_(
        t_like.c.UserID == user_id,
        t_like.c.Score != Like.MEH.name
    )).distinct()
    with get_connection() as conn:
        res = conn.execute(q).fetchall()

    res = [Language[e['Language']] for e in res]
    return res

def liked_items(user_id, lang, score=Like.UP):
    t_feeds = get_table('Feeds')
    t_items = get_table('Items')
    t_like = get_table('Like')

    q = sql.select([
        t_items
    ]).select_from(
        t_items.join(t_feeds)
               .join(t_like)
    ).where(sql.and_(
        t_like.c.UserID == user_id,
        t_feeds.c.Language == lang.name,
        t_like.c.Score == score.name
    ))
    with get_connection() as conn:
        return conn.execute(q).fetchall()

def disliked_items(user_id, lang):
    return liked_items(user_id, lang, Like.DOWN)

def unscored_items(user_id, lang, tags, start, finish, last=None):
    return updated_items(user_id, [lang], tags, start, finish, last, magic=True, unscored=True)
