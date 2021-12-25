#!/usr/bin/env python3

import datetime
import html
import lxml
import typing

from .. import req

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

def format_date(page_date, timeunit):
    current_date = datetime.datetime.now()

    ONE_DAY = datetime.timedelta(days=1)
    ONE_WEEK = datetime.timedelta(days=7)
    ONE_MONTH = datetime.timedelta(days=31)

    if timeunit == req.Timeunit.DAY:
        if current_date >= page_date and current_date < page_date + ONE_DAY:
            topnav_title = "Today"
        elif current_date - ONE_DAY >= page_date and current_date - ONE_DAY < page_date + ONE_DAY:
            topnav_title = "Yesterday"
        else:
            topnav_title = page_date.strftime("%a, %d %b %Y")
    elif timeunit == timeunit.WEEK:
        if current_date >= page_date and current_date < page_date + ONE_WEEK:
            topnav_title = "This week"
        elif current_date - ONE_WEEK >= page_date and current_date - ONE_WEEK < page_date + ONE_WEEK:
            topnav_title = "Last week"
        else:
            topnav_title = page_date.strftime("Week %U, %Y")
    elif timeunit == timeunit.MONTH:
        if current_date >= page_date and current_date < (page_date + ONE_MONTH).replace(day=1):
            topnav_title = "This month"
        elif (current_date - ONE_MONTH).replace(day=1) >= page_date and (current_date - ONE_MONTH).replace(day=1) < (page_date + ONE_MONTH).replace(day=1):
            topnav_title = "Last month"
        else:
            topnav_title = page_date.strftime("%B %Y")
    else:
        raise ValueError

    return topnav_title

