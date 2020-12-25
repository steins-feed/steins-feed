#!/usr/bin/env python3

from datetime import datetime, timedelta
from sqlalchemy import func, sql

from . import get_connection, get_table
from .schema import Language

def last_updated():
    conn = get_connection()
    feeds = get_table('Feeds')

    try:
        q = sql.select([func.min(feeds.c.Updated)])
        res = conn.execute(q).fetchone()[0]
        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.utcfromtimestamp(0)

    return res

def last_liked(user_id=None):
    conn = get_connection()
    like = get_table('Like')

    try:
        q = sql.select([func.max(like.c.Updated)])
        if user_id:
            q = q.where(like.c.UserID == user_id)
        res = conn.execute(q).fetchone()[0]
        if res is None:
            raise IndexError
    except IndexError:
        res = datetime.utcfromtimestamp(0)

    return res

def updated_dates(user_id, keys, last=None, limit=None):
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')
    items = get_table('Items')

    feeds_displayed = feeds.join(display)
    items_displayed = items.join(feeds_displayed)
    q = sql.select([
            sql.extract(e.lower(), items.c.Published).label(e) for e in keys
    ]).distinct().select_from(items_displayed)
    q_where = [display.c.UserID == user_id]
    if last:
        q_where.append(items.c.Published < last)
    q = q.where(sql.and_(*q_where))
    q = q.order_by(*[sql.desc(e) for e in keys])
    if limit:
        q = q.limit(limit)

    res = conn.execute(q)
    res = [datetime(*e) for e in res]
    return res

def updated_items(user_id, langs, tags, start, finish, last=None, magic=False):
    conn = get_connection()
    t_feeds = get_table('Feeds')
    t_display = get_table('Display')
    t_tags = get_table('Tags')
    t_tags2feeds = get_table('Tags2Feeds')
    t_items = get_table('Items')
    t_like = get_table('Like')
    t_magic = get_table('Magic')

    q_select = [
            t_items,
            t_feeds.c.Title.label("Feed"),
            t_feeds.c.Language,
            func.coalesce(t_like.c.Score, 0).label("Like")
    ]
    if magic:
        q_select.append(t_magic.c.Score)
    q = sql.select(q_select)

    t_feeds_displayed = t_feeds.join(t_display)
    t_items_displayed = t_items.join(t_feeds_displayed)
    t_items_displayed_tagged = t_items_displayed
    if tags:
        t_items_displayed_tagged = t_items_displayed_tagged.join(t_tags2feeds)
        t_items_displayed_tagged = t_items_displayed_tagged.join(t_tags)
    t_items_displayed_tagged = t_items_displayed_tagged.outerjoin(t_like)
    if magic:
        t_items_displayed_tagged = t_items_displayed_tagged.outerjoin(t_magic)
    q = q.select_from(t_items_displayed_tagged)

    q_where = [
            t_display.c.UserID == user_id,
            t_items.c.Published.between(start, finish),
            t_items.c.Published < last
    ]
    if langs:
        q_lang = [t_feeds.c.Language == Language(e).name for e in langs]
        q_where.append(sql.or_(*q_lang))
    if tags:
        q_tag = [t_tags.c.Name == e for e in tags]
        q_where.append(sql.or_(*q_tag))
    q = q.where(sql.and_(*q_where))

    if magic:
        q = q.order_by(sql.desc(t_magic.c.Score))
    else:
        q = q.order_by(sql.desc(t_items.c.Published))
    return conn.execute(q).fetchall()

def displayed_languages(user_id=None):
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')

    feeds_displayed = feeds.join(display)
    q = sql.select([
            feeds.c.Language
    ]).distinct().select_from(
            feeds_displayed
    )
    if user_id:
        q = q.where(
                display.c.UserID == user_id
        )

    res = conn.execute(q)
    res = [Language[e[0]].value for e in res]
    return res

def displayed_tags(user_id=None):
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')
    tags = get_table('Tags')
    tags2feeds = get_table('Tags2Feeds')

    feeds_displayed = feeds.join(display)
    tags_displayed = feeds_displayed.join(tags2feeds)
    tags_displayed = tags_displayed.join(tags)
    q = sql.select([
            tags
    ]).select_from(
            tags_displayed
    )
    if user_id:
        q = q.where(
                display.c.UserID == user_id
        )

    res = conn.execute(q)
    res = [e['Name'] for e in res]
    return res

def all_feeds():
    conn = get_connection()
    feeds = get_table('Feeds')

    q = sql.select([
        feeds
    ]).order_by(
        sql.collate(feeds.c.Title, 'NOCASE')
    )

    return conn.execute(q).fetchall()

def all_feeds_lang(user_id):
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')

    display_user = (sql.select([display])
                       .where(display.c.UserID == user_id)
                       .alias())

    res = dict()
    for lang_it in all_langs():
        lang_it = Language(lang_it)
        res[lang_it.value] = []

        q_display = sql.select([
                feeds
        ]).select_from(
                feeds.join(display_user)
        ).where(
                feeds.c.Language == lang_it.name
        ).order_by(
            sql.collate(feeds.c.Title, 'NOCASE')
        )
        res[lang_it.value].append(conn.execute(q_display).fetchall())

        q_hide = sql.select([
            feeds
        ]).select_from(
            feeds.outerjoin(display_user)
        ).where(sql.and_(
            feeds.c.Language == lang_it.name,
            display_user.c.UserID == None
        )).order_by(
            sql.collate(feeds.c.Title, 'NOCASE')
        )
        res[lang_it.value].append(conn.execute(q_hide).fetchall())

    return res

def all_langs():
    conn = get_connection()
    feeds = get_table('Feeds')

    q = sql.select([
        feeds.c.Language
    ]).distinct().order_by(
        sql.collate(feeds.c.Language, 'NOCASE')
    )

    res = conn.execute(q)
    res = [Language[e[0]].value for e in res]
    return res

def all_tags(user_id=None):
    conn = get_connection()
    tags = get_table('Tags')

    q = sql.select([tags])
    if user_id:
        q = q.where(tags.c.UserID == user_id)
    q = q.order_by(sql.collate(tags.c.Name, 'NOCASE'))

    return conn.execute(q).fetchall()

def reset_magic(user_id=None):
    conn = get_connection()
    magic = get_table('Magic')

    q = magic.delete()
    if user_id:
        q = q.where(magic.c.UserID == user_id)
    conn.execute(q)
