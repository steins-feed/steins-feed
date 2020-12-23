#!/usr/bin/env python3

from lxml import etree
import sqlalchemy.sql as sql

from . import get_connection, get_table
from .schema import LANG

ENC = 'utf-8'

def read_xml(f):
    conn = get_connection()
    feeds = get_table('Feeds')

    tree = etree.parse(f)
    root = tree.getroot()
    ins_rows = []

    for feed_it in root.xpath("feed"):
        title = feed_it.xpath("title")[0].text
        link = feed_it.xpath("link")[0].text
        lang = LANG(feed_it.xpath("lang")[0].text).name

        ins_rows.append(dict(zip(
                ['Title', 'Link', 'Language'],
                [title, link, lang]
        )))

    ins = feeds.insert()
    ins = ins.prefix_with("OR IGNORE", dialect='sqlite')
    conn.execute(ins, ins_rows)

def write_xml(f):
    conn = get_connection()
    feeds = get_table('Feeds')

    q = (sql.select([feeds])
            .order_by(sql.collate(feeds.c.Title, 'NOCASE')))

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
            encoding=ENC,
            pretty_print=True
    )
    f.write(s.decode(ENC))
