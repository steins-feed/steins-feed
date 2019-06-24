#!/usr/bin/env python3

from html import unescape
from lxml import html
from lxml.html import builder as E

from steins_lang import lang_list
from steins_sql import get_cursor

def preamble(title):
    tree = E.HTML()

    head = E.HEAD()
    meta_it = E.META(charset="UTF-8")
    head.append(meta_it)
    meta_it = E.META(name="viewport", content="width=device-width, initial-scale=1.0")
    head.append(meta_it)
    link_it = E.LINK(rel="stylesheet", type="text/css", href="/steins-feed/index.css")
    head.append(link_it)
    title_it = E.TITLE()
    title_it.text = title
    head.append(title_it)

    body = E.BODY()

    tree.append(head)
    tree.append(body)
    return tree, head, body

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

def top_nav(title):
    tree = E.DIV(E.CLASS("topnav"))
    h_it = E.H1()
    h_it.text = title
    span_it = E.SPAN(E.CLASS("scroll"))
    h_it.append(span_it)
    span_it = E.SPAN(E.CLASS("onclick"), onclick="open_menu()")
    span_it.text = unescape("&#9776;")
    h_it.append(span_it)
    tree.append(h_it)

    return tree

def side_nav_nav(user, lang, page_no, dates):
    # Navigation.
    h_it = E.H1(E.CLASS("sidenav"))

    if len(dates) <= 1:
        h_it.text = unescape("&nbsp;")
    else:
        if not page_no <= 0:
            form_it = E.FORM(method="get", action="/steins-feed/index.php")
            input_it = E.INPUT(type='hidden', name="user", value=user)
            form_it.append(input_it)
            input_it = E.INPUT(type='hidden', name="lang", value=lang)
            form_it.append(input_it)
            input_it = E.INPUT(type='hidden', name="page", value=str(page_no-1))
            form_it.append(input_it)
            input_it = E.INPUT(type='submit', value=unescape("&larr;"))
            form_it.append(input_it)
            h_it.append(form_it)
        if not page_no >= len(dates) - 1:
            form_it = E.FORM(method="get", action="/steins-feed/index.php")
            input_it = E.INPUT(type='hidden', name="user", value=user)
            form_it.append(input_it)
            input_it = E.INPUT(type='hidden', name="lang", value=lang)
            form_it.append(input_it)
            input_it = E.INPUT(type='hidden', name="page", value=str(page_no+1))
            form_it.append(input_it)
            input_it = E.INPUT(type='submit', value=unescape("&rarr;"))
            form_it.append(input_it)
            h_it.append(form_it)

    span_it = E.SPAN(E.CLASS("onclick"), onclick="close_menu()")
    span_it.text = unescape("&times;")
    h_it.append(span_it)

    return h_it

def side_nav_disp(user, lang, page_no, feed, clf):
    form_it = E.FORM(method='get', action="/steins-feed/index.php")

    # Language.
    form_it.append(E.P("Language:"))
    langs = ['International']
    langs += [e[0] for e in get_cursor().execute("SELECT DISTINCT Language FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE {}=1".format(user)).fetchall()]
    for lang_it in langs:
        input_it = E.INPUT(type='radio', name="lang", value=lang_it)
        if lang_it == lang:
            input_it.set('checked')
        input_it.tail = lang_it
        form_it.append(input_it)
        form_it.append(E.BR())

    # Feed.
    form_it.append(E.P("Feed:"))
    for feed_it in ['Full', 'Magic', 'Surprise']:
        input_it = E.INPUT(type='radio', name="feed", value=feed_it)
        if feed_it == feed:
            input_it.set('checked')
        input_it.tail = feed_it
        form_it.append(input_it)
        form_it.append(E.BR())

    # Algorithm.
    form_it.append(E.P("Algorithm:"))
    for clf_it in ['Naive Bayes', 'Logistic Regression', 'SVM', 'Linear SVM']:
        input_it = E.INPUT(type='radio', name="clf", value=clf_it)
        if clf_it == clf:
            input_it.set('checked')
        input_it.tail = clf_it
        form_it.append(input_it)
        form_it.append(E.BR())

    # Button.
    p_it = E.P()
    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='hidden', name="page", value=str(page_no))
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Display")
    p_it.append(input_it)
    form_it.append(p_it)

    return form_it

def side_nav_rep(user, clf):
    # Report.
    form_it = E.FORM(method='get', action="/steins-feed/analysis.php")
    p_it = E.P()

    select_it = E.SELECT(name="clf")
    for clf_it in ["Naive Bayes", "Logistic Regression", "SVM", "Linear SVM"]:
        option_it = E.OPTION(value=clf_it)
        option_it.text = clf_it
        if clf_it == clf:
            option_it.set('selected')
        select_it.append(option_it)
    p_it.append(select_it)

    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Report")
    p_it.append(input_it)

    form_it.append(p_it)
    return form_it

def side_nav(user='nobody', lang='International', page_no=0, feed='Full', clf='Naive Bayes', dates=[]):
    tree = E.DIV(E.CLASS("sidenav"), id="sidenav")
    tree.append(side_nav_nav(user, lang, page_no, dates))
    tree.append(side_nav_disp(user, lang, page_no, feed, clf))
    tree.append(E.HR())
    tree.append(side_nav_rep(user, clf))
    tree.append(E.HR())

    # Statistics.
    p_it = E.P()
    a_it = E.A(href="/steins-feed/statistics.php?user={}".format(user))
    a_it.text = "Statistics"
    p_it.append(a_it)
    tree.append(p_it)

    # Settings.
    p_it = E.P()
    a_it = E.A(href="/steins-feed/settings.php?user={}".format(user))
    a_it.text = "Settings"
    p_it.append(a_it)
    tree.append(p_it)

    return tree

def feed_node(user, item_id, like=0, score=None):
    c = get_cursor()
    item_it = c.execute("SELECT * FROM Items WHERE ItemID=?", (item_id, )).fetchone()

    tree = E.DIV()

    h_it = E.H2()
    a_it = E.A(target="_blank", rel="noopener noreferrer", href=unescape(item_it['Link']))
    span_it = E.SPAN(id="title_{}".format(item_it['ItemID']))
    span_it.text = unescape(item_it['Title'])
    a_it.append(span_it)
    h_it.append(a_it)
    tree.append(h_it)

    p_it = E.P()
    if score is None:
        p_it.text = "Source: {}. Published: {}.".format(unescape(item_it['Source']), item_it['Published'])
    else:
        p_it.text = "Source: {}. Published: {}. Score: {:.2f}.\n".format(unescape(item_it['Source']), item_it['Published'], score)
    tree.append(p_it)

    summary_it = E.DIV(id="summary_{}".format(item_it['ItemID']))
    summary_it.append(html.fromstring(unescape(item_it['Summary'])))
    tree.append(summary_it)

    p_it = E.P()

    form_it = E.FORM(target="foo", method="post", action="/steins-feed/like.php")
    input_it = E.INPUT(type='hidden', name="id", value=str(item_it['ItemID']))
    form_it.append(input_it)
    input_it = E.INPUT(type='hidden', name="user", value=user)
    form_it.append(input_it)
    if like == 1:
        input_it = E.INPUT(E.CLASS("liked"), type='submit', id="like_{}".format(item_it['ItemID']), name="submit", value="Like", onclick="set_color_like({})".format(item_it['ItemID']))
    else:
        input_it = E.INPUT(E.CLASS("like"), type='submit', id="like_{}".format(item_it['ItemID']), name="submit", value="Like", onclick="set_color_like({})".format(item_it['ItemID']))
    form_it.append(input_it)
    p_it.append(form_it)

    form_it = E.FORM(target="foo", method="post", action="/steins-feed/like.php")
    input_it = E.INPUT(type='hidden', name="id", value=str(item_it['ItemID']))
    form_it.append(input_it)
    input_it = E.INPUT(type='hidden', name="user", value=user)
    form_it.append(input_it)
    if like == -1:
        input_it = E.INPUT(E.CLASS("disliked"), type='submit', id="dislike_{}".format(item_it['ItemID']), name="submit", value="Dislike", onclick="set_color_dislike({})".format(item_it['ItemID']))
    else:
        input_it = E.INPUT(E.CLASS("dislike"), type='submit', id="dislike_{}".format(item_it['ItemID']), name="submit", value="Dislike", onclick="set_color_dislike({})".format(item_it['ItemID']))
    form_it.append(input_it)
    p_it.append(form_it)

    input_it = E.BUTTON(onclick="highlight({})".format(item_it['ItemID']))
    input_it.text = "Highlight"
    p_it.append(input_it)

    tree.append(p_it)
    return tree
