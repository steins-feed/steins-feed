#!/usr/bin/env python3

import html
import lxml
import re
import typing

from magic import io as magic_io
from model.orm import items as orm_items
from model.orm import users as orm_users
from model.schema import feeds as schema_feeds

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

token_pattern = r"\b{}\b(?![^<]*>)"

def highlight(
    user: orm_users.User,
    item: orm_items.Item,
    lang: schema_feeds.Language,
) -> typing.Tuple[str, str]:
    title = item.Title
    summary = item.Summary
    pipeline = magic_io.read_classifier(user, lang)

    words = extract_words(item.Title, item.Summary)
    coeffs = pipeline.predict_proba(words)
    scores = 2. * coeffs[:, 1] - 1.

    for word_it, score_it in zip(words, scores):
        if abs(score_it) < 0.5:
            continue

        word_pattern = token_pattern.format(word_it)
        word_tooltip = wrap_tooltip(word_it, score_it)

        prog = re.compile(word_pattern)
        title = prog.sub(word_tooltip, title)
        summary = prog.sub(word_tooltip, summary)

    return title, summary

extract_pattern = token_pattern.format(r"\w+")
extract_prog = re.compile(extract_pattern)

def extract_words(*s: str) -> typing.Set[str]:
    return set(e for s_it in s for e in extract_prog.findall(s_it))

def wrap_tooltip(word: str, score: float) -> str:
    marked_word = f"<mark>{word}</mark>"
    tipped_score = f"<span class=\"tooltiptext\">{score: .2f}</span>"

    return (
        "<span class=\"tooltip\">"
        + marked_word
        + tipped_score
        + "</span>"
    )

