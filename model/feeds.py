#!/usr/bin/env python3

from lxml import etree
import sqlalchemy as sqla
import sqlalchemy.sql as sql

from .database import connect, get_table

def read_xml(f):
    conn = connect()
    feeds = get_table('Feeds')

    tree = etree.parse(f)
    root = tree.getroot()
    for feed_it in root.xpath("feed"):
        title = feed_it.xpath("title")[0].text
        link = feed_it.xpath("link")[0].text
        lang = feed_it.xpath("lang")[0].text

        ins = feeds.insert().values(Title=title, Link=link, Language=lang)
        ins = ins.prefix_with("OR IGNORE", dialect='sqlite')
        conn.execute(ins)

def write_xml(f):
    conn = connect()
    feeds = get_table('Feeds')

    sel = sql.select([feeds])
    res = conn.execute(sel)

    root = etree.Element("root")
    for row_it in res:
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

    s = etree.tostring(root, xml_declaration=True, pretty_print=True)
    f.write(s.decode())
