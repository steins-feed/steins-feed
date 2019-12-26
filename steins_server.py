#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import lxml
from lxml.html import builder as E
import os
import time
from urllib.parse import urlsplit, parse_qsl
from xml.sax.saxutils import escape

from steins_feed import handle_page
from steins_html import preamble, side_nav, top_nav, select_lang
from steins_sql import get_connection, get_cursor, add_feed, delete_feed, init_feeds

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

def handle_load_config(user):
    init_feeds(dir_path + os.sep + "tmp_feeds.xml", user)

def handle_export_config(user):
    c = get_cursor()

    with open("tmp_feeds.xml", 'w', encoding='utf-8') as f:
        f.write("<?xml version=\"1.0\"?>\n\n")
        f.write("<root>\n")
        for feed_it in c.execute("SELECT Feeds.*, Display.{} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID".format(user)).fetchall():
            f.write("    <feed>\n")
            f.write("        <title>{}</title>\n".format(escape(feed_it['Title'])))
            f.write("        <link>{}</link>\n".format(escape(feed_it['Link'])))
            f.write("        <disp>{}</disp>\n".format(feed_it[user]))
            f.write("        <lang>{}</lang>\n".format(escape(feed_it['Language'])))
            f.write("        <summary>{}</summary>\n".format(feed_it['Summary']))
            f.write("    </feed>\n")
        f.write("</root>\n")

def handle_settings(user):
    c = get_cursor()

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

    for lang_it in [e[0] for e in c.execute("SELECT DISTINCT Language FROM Feeds ORDER BY Language").fetchall()]:
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

    return lxml.html.tostring(tree, doctype="<!DOCTYPE html>", pretty_print=True).decode('utf-8')

def handle_statistics(user):
    c = get_cursor()

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

    return lxml.html.tostring(tree, doctype="<!DOCTYPE html>", pretty_print=True).decode('utf-8')

class SteinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.path = self.path.replace("/steins-feed", "")

        # Generate page.
        if self.path == "/":
            self.path += "index.php"
            self.do_GET()
        elif self.path == "/index.php":
            self.path += "?page=0"
            self.do_GET()
        elif "/index.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_page(qd['user'], qd['lang'], qd['page'])
            self.wfile.write(s.encode('utf-8'))
        elif self.path == "/favicon.ico":
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()

            file_path = dir_path + os.sep + self.path
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == "/settings.php":
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_settings(qd)
            self.wfile.write(s.encode('utf-8'))
        elif self.path == "/statistics.php":
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_statistics(qd)
            self.wfile.write(s.encode('utf-8'))
        elif "/naive_bayes.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_magic(qd)
            self.wfile.write(s.encode('utf-8'))
        elif "/naive_bayes_surprise.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            #s = handle_surprise(qd)
            s = handle_magic(qd)
            self.wfile.write(s.encode('utf-8'))
        elif "/logistic_regression.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_magic(qd, 'Logistic Regression')
            self.wfile.write(s.encode('utf-8'))
        elif "/logistic_regression_surprise.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            #s = handle_surprise(qd, 'Logistic Regression')
            s = handle_magic(qd, 'Logistic Regression')
            self.wfile.write(s.encode('utf-8'))

    def do_POST(self):
        self.path = self.path.replace("/steins-feed", "")

        # Feeds.
        if self.path == "/display_feeds.php":
            qlen = int(self.headers.get('content-length'))
            qs = self.rfile.read(qlen).decode('utf-8')
            qd = dict(parse_qsl(qs))
            handle_display_feeds(qd)
            self.send_response(204)
            self.end_headers()

            self.path = "/"
            self.do_GET()
        # Add feed.
        elif self.path == "/add_feed.php":
            qlen = int(self.headers.get('content-length'))
            qs = self.rfile.read(qlen).decode('utf-8')
            qd = dict(parse_qsl(qs))
            add_feed(qd['title'], qd['link'], qd['disp'], qd['lang'], qd['summary'], qd['user'])
            self.send_response(204)
            self.end_headers()

            self.path = "/settings.php"
            self.do_GET()
        # Delete feed.
        elif self.path == "/delete_feed.php":
            qlen = int(self.headers.get('content-length'))
            qs = self.rfile.read(qlen).decode('utf-8')
            qd = dict(parse_qsl(qs))
            delete_feed(int(qd['feed']))
            self.send_response(204)
            self.end_headers()

            self.path = "/settings.php"
            self.do_GET()
        # Load config.
        elif "/load_config.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = self.rfile.read(qlen).decode('utf-8')
            qd = dict(parse_qsl(qs))
            file_name = "tmp_feeds.xml"
            file_path = dir_path + os.sep + file_name
            with open(file_path, 'w') as f:
                f.write(qd['files'].values()[0])
            handle_load_config(qd['user'])
            self.send_response(204)
            self.end_headers()

            self.path = "/settings.php"
            self.do_GET()
        # Export config.
        if "/export_config.php" in self.path:
            self.send_response(200)
            self.send_header("Content-Description", "File Transfer")
            self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Disposition", "attachment; filename=tmp_feeds.xml")
            self.end_headers()

            qs = self.rfile.read(qlen).decode('utf-8')
            qd = dict(parse_qsl(qs))
            handle_export_config(qd['user'])
            with open("tmp_feeds.xml", 'r', 'utf-8') as f:
                self.wfile.write(f.read().encode('utf-8'))
        # Like.
        elif "/like.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = self.rfile.read(qlen).decode('utf-8')
            qd = dict(parse_qsl(qs))
            handle_like(qd)
            self.send_response(204)
            self.end_headers()
        # Dislike.
        elif "/dislike.php" in self.path:
            qlen = int(self.headers.get('content-length'))
            qs = self.rfile.read(qlen).decode('utf-8')
            qd = dict(parse_qsl(qs))
            handle_like(qd, -1)
            self.send_response(204)
            self.end_headers()

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

if __name__ == "__main__":
    from steins_sql import close_connection

    steins_run()
    close_connection()
