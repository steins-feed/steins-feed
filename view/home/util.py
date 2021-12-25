#!/usr/bin/env python3

import html
import lxml
import typing

def clean_summary(s: str) -> str:
    try:
        tree = lxml.html.fromstring(s)
    except lxml.etree.ParserError:
        return ""
    except lxml.etree.XMLSyntaxError:
        return ""

    # Penalize if full document.
    tags = ['h' + str(e + 1) for e in range(6)];
    for tag_it in tags:
        elems = tree.xpath("//{}".format(tag_it))
        if len(elems) > 0:
            return ""

    # Strip tags and content.
    tags = ['figure', 'img']
    if tree.tag in tags:
        return ""
    lxml.etree.strip_elements(tree, *tags, with_tail=False)

    # Strip classes and content.
    classes = ['instagram', 'tiktok', 'twitter']
    for class_it in classes:
        elems = tree.xpath("//*[contains(@class, '" + class_it + "')]")
        for elem_it in reversed(elems):
            elem_it.drop_tree()

    # Strip empty tags.
    tags = ['div', 'p', 'span']
    empty_leaves(tree, tags)

    return html.unescape(
        lxml.html.tostring(tree, encoding='unicode', method='html')
    )

def empty_leaves(
    e: lxml.etree.Element,
    tags: typing.List[str] = None,
):
    for e_it in reversed(list(e)):
        empty_leaves(e_it)

    if len(e) == 0 and not e.text and not e.tail and (
        tags is None or e.tag in tags
    ):
        e.drop_tree()

