#!/usr/bin/env python3

import html
from lxml.html import fromstring, builder as E

from steins_config import lang_list, clf_dict
from steins_sql import get_cursor

ENCODING = 'utf-8'

def encode(s):
    return s.encode(ENCODING)

def decode(s):
    return s.decode(ENCODING)

def unescape(s):
    return html.unescape(html.unescape(s))

def select_lang(feed_id=None, selected='English'):
    tree = E.SELECT(name="lang")
    if not feed_id is None:
        tree.name = "lang_{}".format(feed_id)

    for lang_it in lang_list:
        option_it = E.OPTION(value=lang_it)
        option_it.text = lang_it
        if lang_it == selected:
            option_it.set('selected')
        tree.append(option_it)

    return tree
