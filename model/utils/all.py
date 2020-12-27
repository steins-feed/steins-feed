#!/usr/bin/env python3

from datetime import datetime
from sqlalchemy import func, sql

from .. import get_connection, get_table
from ..schema import Language

def all_feeds():
    conn = get_connection()
    feeds = get_table('Feeds')

    q = sql.select([
        feeds
    ]).order_by(
        sql.collate(feeds.c.Title, 'NOCASE')
    )

    return conn.execute(q).fetchall()

def all_tags(user_id):
    conn = get_connection()
    tags = get_table('Tags')

    q = sql.select([
        tags
    ]).where(
        tags.c.UserID == user_id
    ).order_by(
        sql.collate(tags.c.Name, 'NOCASE')
    )

    return conn.execute(q).fetchall()

def displayed_languages(user_id):
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')

    q = sql.select([
            feeds.c.Language
    ]).distinct().select_from(
            feeds.join(display)
    ).where(
            display.c.UserID == user_id
    )

    res = conn.execute(q)
    res = [Language[e['Language']] for e in res]
    return res

def displayed_tags(user_id):
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')
    tags = get_table('Tags')
    tags2feeds = get_table('Tags2Feeds')

    q = sql.select([
            tags.c.Name
    ]).select_from(
            feeds.join(display)
                 .join(tags2feeds)
                 .join(tags)
    ).where(
            display.c.UserID == user_id
    )

    res = conn.execute(q)
    res = [e['Name'] for e in res]
    return res

def updated_dates(user_id, keys, last=None, limit=None):
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')
    items = get_table('Items')

    q = sql.select([
            sql.extract(e.lower(), items.c.Published).label(e) for e in keys
    ]).distinct().select_from(
            items.join(feeds)
                 .join(display)
    )
    q_where = [display.c.UserID == user_id]
    if last:
        q_where.append(items.c.Published < last)
    q = q.where(sql.and_(*q_where))
    q = q.order_by(*[sql.desc(e) for e in keys])
    if limit:
        q = q.limit(limit)

    date_string, format_string = keys2strings(keys)
    tuple2datetime = lambda x: datetime.strptime(
            date_string.format(*x),
            format_string
    )

    res = conn.execute(q)
    res = [tuple2datetime(e) for e in res]
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
    if tags:
        t_items_displayed = t_items_displayed.join(t_tags2feeds)
        t_items_displayed = t_items_displayed.join(t_tags)
    t_items_displayed = t_items_displayed.outerjoin(t_like)
    if magic:
        t_items_displayed = t_items_displayed.outerjoin(t_magic)
    q = q.select_from(t_items_displayed)

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

def keys2strings(keys):
    date_string = "{}"
    format_string = "%Y"

    for key_it in keys[1:]:
        if key_it == "Month":
            date_string += "-{}"
            format_string += "-%m"
        elif key_it == "Week":
            date_string += "-{}"
            format_string += "-%U"
        elif key_it == "Day":
            date_string += "-{}"
            format_string += "-%d"

    if keys[-1] == "Month":
        date_string += "-1"
        format_string += "-%d"
    elif keys[-1] == "Week":
        date_string += "-0"
        format_string += "-%w"

    return date_string, format_string
