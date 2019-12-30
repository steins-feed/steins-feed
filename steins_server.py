#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from lxml.html import tostring, builder as E
import os
import time
from urllib.parse import urlsplit, parse_qsl
from xml.sax.saxutils import escape

from steins_feed import handle_page
from steins_html import decode, encode, preamble, side_nav, top_nav, select_lang
from steins_magic import handle_analysis, handle_highlight
from steins_sql import get_connection, get_cursor, add_feed, delete_feed, add_user, rename_user, delete_user
from steins_xml import handle_load_config, handle_export_config

dir_path = os.path.dirname(os.path.abspath(__file__))

PORT = 8000

def handle_like(qd):
    conn = get_connection()
    c = conn.cursor()

    user = qd['user']
    item_id = int(qd['id'])
    submit = qd['submit']

    if submit == "Like":
        val = 1
    if submit == "Dislike":
        val = -1
    row_val = c.execute("SELECT {} FROM Like WHERE ItemID=?".format(user), (item_id, )).fetchone()[0]
    if row_val == val:
        c.execute("UPDATE Like SET {}=0 WHERE ItemID=?".format(user), (item_id, ))
    else:
        c.execute("UPDATE Like SET {}=? WHERE ItemID=?".format(user), (val, item_id, ))

    conn.commit()

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

        for feed_it in c.execute("SELECT Feeds.*, Display.{} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID WHERE Language='{}' ORDER BY Title COLLATE NOCASE".format(user, lang_it)).fetchall():
            input_it = E.INPUT(type='checkbox', name=str(feed_it['ItemID']))
            form_it.append(input_it)
            if feed_it[user] != 0:
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
        option_it = E.OPTION(value=str(feed_it['ItemID']))
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

def handle_statistics(qd):
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

    # Likes.
    likes = c.execute("SELECT Items.*, Like.{0} FROM Items INNER JOIN Like ON Items.ItemID=Like.ItemID WHERE {0}=1 ORDER BY Published DESC".format(user, user)).fetchall()

    h_it = E.H2()
    h_it.text = "Likes"
    div_it.append(h_it)

    p_it = E.P()
    p_it.text = "{} likes.".format(len(likes))
    div_it.append(p_it)

    ul_it = E.UL()
    div_it.append(ul_it)

    for row_it in likes:
        datestamp = time.strftime("%A, %d %B %Y", time.strptime(row_it['Published'], "%Y-%m-%d %H:%M:%S GMT"))

        li_it = E.LI()
        ul_it.append(li_it)
        li_it.text = "{}: ".format(row_it['Source'])

        a_it = E.A(href=row_it['Link'])
        a_it.text = row_it['Title']
        a_it.tail = " ({})".format(datestamp)
        li_it.append(a_it)

    div_it.append(E.HR())

    #--------------------------------------------------------------------------

    # Dislikes.
    dislikes = c.execute("SELECT Items.*, Like.{0} FROM Items INNER JOIN Like ON Items.ItemID=Like.ItemID WHERE {0}=-1 ORDER BY Published DESC".format(user, user)).fetchall()

    h_it = E.H2()
    h_it.text = "Dislikes"
    div_it.append(h_it)

    p_it = E.P()
    p_it.text = "{} dislikes.".format(len(dislikes))
    div_it.append(p_it)

    ul_it = E.UL()
    div_it.append(ul_it)

    for row_it in dislikes:
        datestamp = time.strftime("%A, %d %B %Y", time.strptime(row_it['Published'], "%Y-%m-%d %H:%M:%S GMT"))

        li_it = E.LI()
        ul_it.append(li_it)
        li_it.text = "{}: ".format(row_it['Source'])

        a_it = E.A(href=row_it['Link'])
        a_it.text = row_it['Title']
        a_it.tail = " ({})".format(datestamp)
        li_it.append(a_it)

    #--------------------------------------------------------------------------

    return decode(tostring(tree, doctype="<!DOCTYPE html>", pretty_print=True))

class SteinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.path = self.path.replace("/steins-feed", "")

        # Generate page.
        if self.path == "/":
            self.path += "index.php"
            self.do_GET()
        elif self.path == "/index.php":
            self.path += "?user=nobody"
            self.do_GET()
        elif "/index.php" in self.path and "user=" not in self.path:
            self.path += "&user=nobody"
            self.do_GET()
        elif "/index.php" in self.path and "lang=" not in self.path:
            self.path += "&lang=International"
            self.do_GET()
        elif "/index.php" in self.path and "page=" not in self.path:
            self.path += "&page=0"
            self.do_GET()
        elif "/index.php" in self.path and "feed=" not in self.path:
            self.path += "&feed=Full"
            self.do_GET()
        elif "/index.php" in self.path and "clf=" not in self.path:
            self.path += "&clf=Naive+Bayes"
            self.do_GET()
        elif "/index.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_page(qd)
            self.wfile.write(encode(s))
        elif self.path == "/index.css":
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()

            file_path = dir_path + os.sep + self.path
            with open(file_path, 'r') as f:
                self.wfile.write(encode(f.read()))
        elif self.path == "/favicon.ico":
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()

            file_path = dir_path + os.sep + self.path
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        elif "/settings.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_settings(qd)
            self.wfile.write(encode(s))
        elif "/statistics.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_statistics(qd)
            self.wfile.write(encode(s))
        elif "/analysis.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_analysis(qd)
            self.wfile.write(encode(s))

    def do_POST(self):
        self.path = self.path.replace("/steins-feed", "")

        # Feeds.
        if "/display_feeds.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs, keep_blank_values=True))
            handle_display_feeds(qd)

            self.path = "/index.php?user={}".format(qd['user'])
            self.do_GET()
        # Add feed.
        elif "/add_feed.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            add_feed(qd['title'], qd['link'], qd['lang'], qd['disp'], qd['summary'], qd['user'])
            get_connection().commit()

            self.path = "/settings.php?user={}".format(qd['user'])
            self.do_GET()
        # Delete feed.
        elif "/delete_feed.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            delete_feed(int(qd['feed']))

            self.path = "/settings.php?user={}".format(qd['user'])
            self.do_GET()
        # Load config.
        elif "/load_config.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            file_name = "tmp_feeds.xml"
            file_path = dir_path + os.sep + file_name
            with open(file_path, 'w') as f:
                f.write(qd['files'].values()[0])
            handle_load_config(qd)

            self.path = "/settings.php?user={}".format(qd['user'])
            self.do_GET()
        # Export config.
        if "/export_config.php" in self.path:
            self.send_response(200)
            self.send_header("Content-Description", "File Transfer")
            self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Disposition", "attachment; filename=tmp_feeds.xml")
            self.end_headers()

            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            handle_export_config(qd)
            with open("tmp_feeds.xml", 'r') as f:
                self.wfile.write(encode(s))
        # Like.
        elif "/like.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            handle_like(qd)
            self.send_response(200)
            self.end_headers()
        # Highlight.
        elif "/highlight.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            self.send_response(200)
            self.end_headers()
            self.wfile.write(encode(handle_highlight(qd)))
        # Add user.
        elif "/add_user.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            add_user(qd['name'])

            self.path = "/settings.php?user={}".format(qd['name'])
            self.do_GET()
        # Rename user.
        elif "/rename_user.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            rename_user(qd['user'], qd['name'])

            self.path = "/settings.php?user={}".format(qd['name'])
            self.do_GET()
        # Delete user.
        elif "/delete_user.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = decode(self.rfile.read(qlen))
            qd = dict(parse_qsl(qs))
            delete_user(qd['user'])

            self.path = "/index.php?user={}".format('nobody')
            self.do_GET()

def steins_run():
    global PORT
    port = PORT

    while True:
        try:
            server = HTTPServer(('localhost', port), SteinsHandler)
            break
        except OSError:
            port += 2

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

    PORT = port
