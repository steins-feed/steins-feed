#!/usr/bin/env python3

from lxml import etree
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

def get_tree_from_session(item_link):
    session = get_session()
    page = session.get(item_link)
    tree = etree.fromstring(page.text.encode())
    return tree
