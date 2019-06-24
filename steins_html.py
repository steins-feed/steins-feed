#!/usr/bin/env python3

from html import unescape
from lxml.html import builder as E

from steins_lang import lang_list
from steins_sql import get_cursor

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

def side_nav(user='nobody', lang='International', page_no=0, feed='Full', clf='Naive Bayes', dates=[]):
    tree = E.DIV(E.CLASS("sidenav"), id="sidenav")
    c = get_cursor()

    # Navigation.
    h_it = E.H1(E.CLASS("sidenav"))
    if len(dates) <= 1:
        h_it.text = unescape("&nbsp;")
    else:
        if not page_no <= 0:
            form_it = E.FORM()
            input_it = E.INPUT(type='hidden', name="user", value=user)
            form_it.append(input_it)
            input_it = E.INPUT(type='hidden', name="lang", value=lang)
            form_it.append(input_it)
            input_it = E.INPUT(type='hidden', name="page", value=str(page_no-1))
            form_it.append(input_it)
            input_it = E.INPUT(type='submit', formmethod="get", formaction="/steins-feed/index.php", value=unescape("&larr;"))
            form_it.append(input_it)
            h_it.append(form_it)
        if not page_no >= len(dates) - 1:
            form_it = E.FORM()
            input_it = E.INPUT(type='hidden', name="user", value=user)
            form_it.append(input_it)
            input_it = E.INPUT(type='hidden', name="lang", value=lang)
            form_it.append(input_it)
            input_it = E.INPUT(type='hidden', name="page", value=str(page_no+1))
            form_it.append(input_it)
            input_it = E.INPUT(type='submit', formmethod="get", formaction="/steins-feed/index.php", value=unescape("&rarr;"))
            form_it.append(input_it)
            h_it.append(form_it)
    span_it = E.SPAN(E.CLASS("onclick"), onclick="close_menu()")
    span_it.text = unescape("&times;")
    h_it.append(span_it)
    tree.append(h_it)

    form_it = E.FORM()

    # Language.
    form_it.append(E.P("Language:"))
    langs = ['International']
    langs += [e[0] for e in c.execute("SELECT DISTINCT Language FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE {}=1".format(user)).fetchall()]
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
    input_it = E.INPUT(type='submit', formmethod='get', formaction="/steins-feed/index.php", value="Display")
    p_it.append(input_it)
    form_it.append(p_it)

    tree.append(form_it)
    tree.append(E.HR())
    form_it = E.FORM()

    # Report.
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
    input_it = E.INPUT(type='submit', formmethod='get', formaction="/steins-feed/analysis.php", value="Report")
    p_it.append(input_it)
    form_it.append(p_it)

    tree.append(form_it)
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
