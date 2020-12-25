#!/usr/bin/env python3

from datetime import datetime, timedelta
from sqlalchemy import func, sql

from . import get_connection, get_table

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

def updated_dates(user_id, timeunit, last=None, limit=None):
    if timeunit == "Day":
        order = ["Year", "Month", "Day"]
    elif timeunit == "Week":
        order = ["Year", "Week"]
    elif timeunit == "Month":
        order = ["Year", "Month"]
    else:
        raise ValueError

    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')
    items = get_table('Items')

    feeds_displayed = feeds.join(display)
    items_displayed = items.join(feeds_displayed)
    q = sql.select([
            sql.extract(e.lower(), items.c.Published).label(e) for e in order
    ]).distinct().select_from(items_displayed)
    q_where = [display.c.UserID == user_id]
    if last:
        q_where.append(items.c.Published < last)
    q = q.where(sql.and_(*q_where))
    q = q.order_by(*[sql.desc(e) for e in order])
    if limit:
        q = q.limit(limit)

    res = conn.execute(q)
    res = [datetime(*e) for e in res]
    return res

def updated_items(user_id, timeunit, feed, tags_disp, first, last=None):
    conn = get_connection()
    feeds = get_table('Feeds')
    display = get_table('Display')
    tags = get_table('Tags')
    tags2feeds = get_table('Tags2Feeds')
    items = get_table('Items')
    like = get_table('Like')
    magic = get_table('Magic')

    q_select = [
            items,
            feeds.c.Title.label("Feed"),
            feeds.c.Language,
            func.coalesce(like.c.Score, 0).label("Like")
    ]
    if feed != "Full":
        q_select.append(magic.c.Score)
    q = sql.select(q_select)

    feeds_displayed = feeds.join(display)
    items_displayed = items.join(feeds_displayed)
    items_displayed_tagged = items_displayed
    if tags_disp:
        items_displayed_tagged = items_displayed_tagged.join(tags2feeds)
        items_displayed_tagged = items_displayed_tagged.join(tags)
    items_displayed_tagged = items_displayed_tagged.outerjoin(like
    )
    if feed != "Full":
        items_displayed_tagged = items_displayed_tagged.outerjoin(magic)
    q = q.select_from(items_displayed_tagged)

    start_time = first
    if timeunit == "Day":
        finish_time = first + timedelta(days=1)
    elif timeunit == "Week":
        finish_time = first + timedelta(weeks=1)
    elif timeunit == "Month":
        finish_time = first + timedelta(months=1)
        finish_time.replace(days=0)
    q_where = [
            display.c.UserID == user_id,
            items.c.Published.between(start_time, finish_time),
            items.c.Published < last
    ]
    # stmt_lang
    # if tags_disp: stmt_tag
    q = q.where(sql.and_(*q_where))

    if feed == "Full":
        q = q.order_by(sql.desc(items.c.Published))
    else:
        q = q.order_by(sql.desc(magic.c.Score))
    return conn.execute(q).fetchall()

def reset_magic(user_id=None):
    conn = get_connection()
    magic = get_table('Magic')

    q = magic.delete()
    if user_id:
        q = q.where(magic.c.UserID == user_id)
    conn.execute(q)
