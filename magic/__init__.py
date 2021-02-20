#!/usr/bin/env python3

from html import unescape
from lxml import etree, html

def build_feature(row):
    tree = html.fromstring(row['Title'])
    return html.tostring(tree, encoding='unicode', method='text')
