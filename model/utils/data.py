#!/usr/bin/env python3

from sqlalchemy import sql

from .. import get_connection, get_table
from ..schema import Language, Like

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

def all_feeds_lang_disp(user_id):
    feeds = get_table('Feeds')
    display = get_table('Display')

    display_user = (sql.select([display])
                       .where(display.c.UserID == user_id)
                       .alias())

    res = dict()
    for lang_it in all_langs_feeds():
        lang_it = Language(lang_it)
        res[lang_it] = []

        with get_connection() as conn:
            q = sql.select([
                    feeds
            ]).select_from(
                    feeds.join(display_user)
            ).where(
                    feeds.c.Language == lang_it.name
            ).order_by(
                    sql.collate(feeds.c.Title, 'NOCASE')
            )
            res[lang_it].append(conn.execute(q).fetchall())

            q = sql.select([
                    feeds
            ]).select_from(
                    feeds.outerjoin(display_user)
            ).where(sql.and_(
                    feeds.c.Language == lang_it.name,
                    display_user.c.FeedID == None
            )).order_by(
                    sql.collate(feeds.c.Title, 'NOCASE')
            )
            res[lang_it].append(conn.execute(q).fetchall())

    return res

def all_feeds_lang_tag(tag_id):
    feeds = get_table('Feeds')
    tags2feeds = get_table('Tags2Feeds')

    tags2feeds_tag = (sql.select([tags2feeds])
                         .where(tags2feeds.c.TagID == tag_id)
                         .alias())

    res = dict()
    for lang_it in all_langs_feeds():
        lang_it = Language(lang_it)
        res[lang_it] = []

        with get_connection() as conn:
            q = sql.select([
                    feeds
            ]).select_from(
                    feeds.join(tags2feeds_tag)
            ).where(
                    feeds.c.Language == lang_it.name
            ).order_by(
                    sql.collate(feeds.c.Title, 'NOCASE')
            )
            res[lang_it].append(conn.execute(q).fetchall())

            q = sql.select([
                    feeds
            ]).select_from(
                    feeds.outerjoin(tags2feeds_tag)
            ).where(sql.and_(
                    feeds.c.Language == lang_it.name,
                    tags2feeds_tag.c.FeedID == None
            )).order_by(
                    sql.collate(feeds.c.Title, 'NOCASE')
            )
            res[lang_it].append(conn.execute(q).fetchall())

    return res

def all_likes_lang(user_id):
    feeds = get_table('Feeds')
    items = get_table('Items')
    like = get_table('Like')

    q = sql.select([
            items,
            feeds.c.Title.label("Feed")
    ]).select_from(
            items.join(feeds).join(like)
    ).where(sql.and_(
            like.c.UserID == user_id,
            like.c.Score == sql.bindparam("score"),
            feeds.c.Language == sql.bindparam("lang")
    )).order_by(
        sql.desc(items.c.Published)
    )

    res = dict()
    with get_connection() as conn:
        for lang_it in all_langs_feeds():
            lang_it = Language(lang_it)

            res[lang_it] = []
            res[lang_it].append(
                    conn.execute(q, score=Like.UP.name, lang=lang_it.name).fetchall()
            )
            res[lang_it].append(
                    conn.execute(q, score=Like.DOWN.name, lang=lang_it.name).fetchall()
            )

    return res

def all_tags_feed(user_id, feed_id):
    tags = get_table('Tags')
    tags2feeds = get_table('Tags2Feeds')

    res = []
    tags2feeds_feed = (sql.select([tags2feeds])
                         .where(tags2feeds.c.FeedID == feed_id)
                         .alias())

    with get_connection() as conn:
        q = sql.select([
                tags
        ]).select_from(
                tags.join(tags2feeds_feed)
        ).where(
                tags.c.UserID == user_id
        ).order_by(
                sql.collate(tags.c.Name, 'NOCASE')
        )
        res.append(conn.execute(q).fetchall())

        q = sql.select([
                tags
        ]).select_from(
                tags.outerjoin(tags2feeds_feed)
        ).where(sql.and_(
                tags.c.UserID == user_id,
                tags2feeds_feed.c.TagID == None
        )).order_by(
                sql.collate(tags.c.Name, 'NOCASE')
        )
        res.append(conn.execute(q).fetchall())

    return res
