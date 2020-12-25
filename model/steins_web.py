#!/usr/bin/env python3

from lxml import etree, html
import requests

def have_session():
    if 'session' in globals():
        return True
    else:
        return False

def get_session():
    global session
    if not have_session():
        session = requests.Session()
    return session

def get_tree_from_session(item_link, fmt="xml"):
    session = get_session()
    page = session.get(item_link)
    if fmt == "xml":
        tree = etree.fromstring(page.text.encode())
    elif fmt == "html":
        tree = html.fromstring(page.text.encode())
    return tree, page.status_code
