#!/usr/bin/env python3

from lxml import etree
from sqlalchemy import sql

from . import engine, get_table
from .schema import Language

def read_xml(f, user_id=None, tag=None):
    t_feeds = get_table("Feeds")
    t_tags2feeds = get_table("Tags2Feeds")
    t_tags = get_table("Tags")

    tree = etree.parse(f)
    root = tree.getroot()

    rows = []
    for feed_it in root.xpath("feed"):
        rows.append({
            "Title": feed_it.xpath("title")[0].text,
            "Link": feed_it.xpath("link")[0].text,
            "Language": Language(feed_it.xpath("lang")[0].text).name,
        })

    q = t_feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect="sqlite")

    with engine.connect() as conn:
        conn.execute(q, rows)

    if user_id and tag:
        q = t_tags.insert().values(
            UserID=user_id,
            Name=tag,
        )
        q = q.prefix_with("OR IGNORE", dialect="sqlite")

        with engine.connect() as conn:
            conn.execute(q)

        q_select = sql.select([
            t_feeds.c.FeedID,
            t_tags.c.TagID,
        ]).where(sql.and_(
            t_feeds.c.Title == sql.bindparam("Title"),
            t_tags.c.UserID == user_id,
            t_tags.c.Name == tag,
        ))

        q = t_tags2feeds.insert()
        q = q.from_select([q_select.c.FeedID, q_select.c.TagID], q_select)
        q = q.prefix_with("OR IGNORE", dialect="sqlite")

        with engine.connect() as conn:
            conn.execute(q, rows)

def write_xml(f, user_id=None, tag=None):
    feeds = get_table('Feeds')
    tags2feeds = get_table('Tags2Feeds')
    tags = get_table('Tags')

    q = sql.select([feeds])
    if user_id and tag:
        q = q.select_from(
            feeds.join(tags2feeds)
                 .join(tags)
        )
        q = q.where(sql.and_(
            tags.c.UserID == user_id,
            tags.c.Name == tag
        ))
    q = q.order_by(sql.collate(feeds.c.Title, 'NOCASE'))
    with engine.connect() as conn:
        rows = conn.execute(q).fetchall()

    root = etree.Element("root")
    for row_it in rows:
        title_it = etree.Element("title")
        title_it.text = row_it['Title']
        link_it = etree.Element("link")
        link_it.text = row_it['Link']
        lang_it = etree.Element("lang")
        lang_it.text = Language[row_it['Language']].value

        feed_it = etree.Element("feed")
        feed_it.append(title_it)
        feed_it.append(link_it)
        feed_it.append(lang_it)
        root.append(feed_it)

    s = etree.tostring(root,
            encoding='unicode',
            pretty_print=True
    )
    f.write(s)
