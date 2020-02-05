#!/usr/bin/env python3

from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from lxml.html import tostring, builder as E
import os
from urllib.parse import urlsplit, parse_qsl
from xml.sax.saxutils import escape

from steins_sql import get_connection, get_cursor, add_feed, delete_feed, add_user, delete_user

dir_path = os.path.dirname(os.path.abspath(__file__))

PORT = 8000

def handle_display_feeds(qd):
    conn = get_connection()
    c = conn.cursor()

    qd_keys = qd.keys()
    for feed_it in c.execute("SELECT ItemID FROM Feeds").fetchall():
        if str(feed_it[0]) in qd_keys:
            c.execute("UPDATE Display SET {}=1 WHERE ItemID=?".format(qd['user']), (feed_it[0], ))
        else:
            c.execute("UPDATE Display SET {}=0 WHERE ItemID=?".format(qd['user']), (feed_it[0], ))

        if "lang_{}".format(feed_it[0]) in qd_keys:
            c.execute("UPDATE Feeds SET Language=? WHERE ItemID=?", (qd["lang_{}".format(feed_it[0])], feed_it[0]))

    conn.commit()

def handle_settings(qd):
    c = get_cursor()
    user = qd['user']

    #--------------------------------------------------------------------------

    # Preamble.
    tree, head, body = preamble(user)

    #--------------------------------------------------------------------------

    # Scripts.
    for js_it in ["open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js"]:
        script_it = E.SCRIPT()
        with open(dir_path + os.sep + "js" + os.sep + js_it, 'r') as f:
            script_it.text = f.read()
        head.append(script_it)

    #--------------------------------------------------------------------------

    # Top & side navigation menus.
    body.append(top_nav(user))
    body.append(side_nav(user))

    #--------------------------------------------------------------------------

    # Body.
    div_it = E.DIV(E.CLASS("main"))
    body.append(div_it)
    div_it.append(E.HR())

    #--------------------------------------------------------------------------

    # Display feeds.
    form_it = E.FORM(method="post", action="/steins-feed/display_feeds.php")
    div_it.append(form_it)
    div_it.append(E.HR())

    for lang_it in [e[0] for e in c.execute("SELECT DISTINCT Language FROM Feeds ORDER BY Language")]:
        h_it = E.H2()
        h_it.text = "{} feeds".format(lang_it)
        form_it.append(h_it)

        displayed = set([e['FeedID'] for e in c.execute("SELECT FeedID FROM Display WHERE UserID=(SELECT UserID FROM Users WHERE Name=?)", (user, ))])
        for feed_it in c.execute("SELECT * FROM Feeds WHERE Language=? ORDER BY Title COLLATE NOCASE", (lang_it, )).fetchall():
            input_it = E.INPUT(type='checkbox', name=str(feed_it['FeedID']))
            form_it.append(input_it)
            if feed_it['FeedID'] in displayed:
                input_it.set('checked')

            a_it = E.A(href=feed_it['Link'])
            a_it.text = feed_it['Title']
            a_it.tail = " "
            form_it.append(a_it)

            #form_it.append(select_lang(feed_it['ItemID'], feed_it['Language']))
            form_it.append(E.BR())

    p_it = E.P()
    form_it.append(p_it)
    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Display feeds")
    p_it.append(input_it)

    #--------------------------------------------------------------------------

    # Add feed.
    form_it = E.FORM(method='post', action="/steins-feed/add_feed.php")
    div_it.append(form_it)
    div_it.append(E.HR())

    p_it = E.P()
    p_it.text = "Title:"
    p_it.append(E.BR())
    input_it = E.INPUT(type='text', name="title")
    p_it.append(input_it)
    form_it.append(p_it)

    p_it = E.P()
    p_it.text = "Link:"
    p_it.append(E.BR())
    input_it = E.INPUT(type='text', name="link")
    p_it.append(input_it)
    form_it.append(p_it)

    p_it = E.P()
    p_it.text = "Display:"
    p_it.append(E.BR())
    input_it = E.INPUT(type='radio', name="disp", value=str(1))
    input_it.set('checked')
    input_it.tail = "Yes"
    p_it.append(input_it)
    input_it = E.INPUT(type='radio', name="disp", value=str(0))
    input_it.tail = "No"
    p_it.append(input_it)
    form_it.append(p_it)

    p_it = E.P()
    p_it.text = "Language:"
    p_it.append(E.BR())
    p_it.append(select_lang())
    form_it.append(p_it)

    p_it = E.P()
    p_it.text = "Summary:"
    p_it.append(E.BR())
    input_it = E.INPUT(type='radio', name="summary", value=str(0))
    input_it.tail = "No abstract."
    p_it.append(input_it)
    input_it = E.INPUT(type='radio', name="summary", value=str(1))
    input_it.tail = "First paragraph."
    p_it.append(input_it)
    input_it = E.INPUT(type='radio', name="summary", value=str(2))
    input_it.set('checked')
    input_it.tail = "Full abstract."
    p_it.append(input_it)
    form_it.append(p_it)

    p_it = E.P()
    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Add feed")
    p_it.append(input_it)
    form_it.append(p_it)

    #--------------------------------------------------------------------------

    # Delete feed.
    form_it = E.FORM(method='post', action="/steins-feed/delete_feed.php")
    div_it.append(form_it)
    div_it.append(E.HR())

    p_it = E.P()
    select_it = E.SELECT(name="feed")
    p_it.append(select_it)
    form_it.append(p_it)

    for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title COLLATE NOCASE").fetchall():
        option_it = E.OPTION(value=str(feed_it['FeedID']))
        option_it.text = feed_it['Title']
        select_it.append(option_it)

    p_it = E.P()
    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Delete feed")
    p_it.append(input_it)
    form_it.append(p_it)

    #--------------------------------------------------------------------------

    # Load config.
    form_it = E.FORM(method='post', action="/steins-feed/load_config.php", enctype="multipart/form-data")
    div_it.append(form_it)
    div_it.append(E.HR())

    p_it = E.P()
    input_it = E.INPUT(type='file', name="feeds", value="feeds")
    p_it.append(input_it)
    form_it.append(p_it)

    p_it = E.P()
    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Load config")
    p_it.append(input_it)
    form_it.append(p_it)

    #--------------------------------------------------------------------------

    # Export config.
    form_it = E.FORM(method='post', action="/steins-feed/export_config.php")
    div_it.append(form_it)
    div_it.append(E.HR())

    p_it = E.P()
    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Export config")
    p_it.append(input_it)
    form_it.append(p_it)

    #--------------------------------------------------------------------------

    # Add user.
    form_it = E.FORM(method='post', action="/steins-feed/add_user.php")
    div_it.append(form_it)
    div_it.append(E.HR())

    p_it = E.P()
    p_it.text = "Name:"
    p_it.append(E.BR())
    input_it = E.INPUT(type="text", name="name")
    p_it.append(input_it)
    form_it.append(p_it)

    p_it = E.P()
    input_it = E.INPUT(type='submit', value="Add user")
    p_it.append(input_it)
    form_it.append(p_it)

    #--------------------------------------------------------------------------

    # Rename user.
    form_it = E.FORM(method='post', action="/steins-feed/rename_user.php")
    div_it.append(form_it)
    div_it.append(E.HR())

    p_it = E.P()
    p_it.text = "New name:"
    p_it.append(E.BR())
    input_it = E.INPUT(type="text", name="name")
    p_it.append(input_it)
    form_it.append(p_it)

    p_it = E.P()
    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Rename user")
    p_it.append(input_it)
    form_it.append(p_it)

    #--------------------------------------------------------------------------

    # Delete user.
    form_it = E.FORM(method='post', action="/steins-feed/delete_user.php")
    div_it.append(form_it)

    p_it = E.P()
    input_it = E.INPUT(type='hidden', name="user", value=user)
    p_it.append(input_it)
    input_it = E.INPUT(type='submit', value="Delete user", style="background-color:red")
    p_it.append(input_it)
    form_it.append(p_it)

    #--------------------------------------------------------------------------

    return decode(tostring(tree, doctype="<!DOCTYPE html>", pretty_print=True))
