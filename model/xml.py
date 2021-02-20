#!/usr/bin/env python3

from lxml import etree
from sqlalchemy import sql

from . import get_connection, get_table
from .schema import Language

def read_xml(f):
    conn = get_connection()
    feeds = get_table('Feeds')

    tree = etree.parse(f)
    root = tree.getroot()

    rows = []
    for feed_it in root.xpath("feed"):
        title = feed_it.xpath("title")[0].text
        link = feed_it.xpath("link")[0].text
        lang = Language(feed_it.xpath("lang")[0].text).name

        rows.append(dict(zip(
                ['Title', 'Link', 'Language'],
                [title, link, lang]
        )))

    q = feeds.insert()
    q = q.prefix_with("OR IGNORE", dialect='sqlite')
    conn.execute(q, rows)

def write_xml(f):
    conn = get_connection()
    feeds = get_table('Feeds')

    q = sql.select([
            feeds
    ]).order_by(
            sql.collate(feeds.c.Title, 'NOCASE')
    )

    root = etree.Element("root")
    for row_it in conn.execute(q):
        title_it = etree.Element("title")
        title_it.text = row_it['Title']
        link_it = etree.Element("link")
        link_it.text = row_it['Link']
        lang_it = etree.Element("lang")
        lang_it.text = row_it['Language']

        feed_it = etree.Element("feed")
        feed_it.append(title_it)
        feed_it.append(link_it)
        feed_it.append(lang_it)
        root.append(feed_it)

    s = etree.tostring(root,
            xml_declaration=True,
            encoding='unicode',
            pretty_print=True
    )
    f.write(s.decode(ENC))
