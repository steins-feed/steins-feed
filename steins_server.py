#!/usr/bin/env python3

import os
import time

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qsl
from xml.sax.saxutils import escape

from steins_feed import steins_generate_page
from steins_html import select_lang
from steins_magic import steins_learn
from steins_sql import get_connection, get_cursor, add_feed, delete_feed, init_feeds

dir_path = os.path.dirname(os.path.abspath(__file__))

PORT = 8000

def handle_like(qd):
    conn = get_connection()
    c = conn.cursor()

    item_id = int(qd['id'])
    if qd['submit'] == "Like":
        val = 1
    if qd['submit'] == "Dislike":
        val = -1
    row_val = c.execute("SELECT {} FROM Like WHERE ItemID=?".format(qd['user']), (item_id, )).fetchone()[0]
    if row_val == val:
        c.execute("UPDATE Like SET {}=0 WHERE ItemID=?".format(qd['user']), (item_id, ))
    else:
        c.execute("UPDATE Like SET {}=? WHERE ItemID=?".format(qd['user']), (val, item_id, ))

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

def handle_add_feed(qd):
    add_feed(qd['title'], qd['link'], qd['disp'], qd['lang'], qd['summary'], qd['user'])

def handle_delete_feed(qd):
    delete_feed(int(qd['feed']), qd['user'])

def handle_load_config(qd):
    init_feeds(dir_path + os.sep + "tmp_feeds.xml", qd['user'])

def handle_export_config(qd):
    c = get_cursor()

    with open("tmp_feeds.xml", 'w', encoding='utf-8') as f:
        f.write("<?xml version=\"1.0\"?>\n\n")
        f.write("<root>\n")
        for feed_it in c.execute("SELECT Feeds.*, Display.{} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID".format(qd['user'])).fetchall():
            f.write("    <feed>\n")
            f.write("        <title>{}</title>\n".format(escape(feed_it['Title'])))
            f.write("        <link>{}</link>\n".format(escape(feed_it['Link'])))
            f.write("        <disp>{}</disp>\n".format(feed_it[qd['user']]))
            f.write("        <lang>{}</lang>\n".format(escape(feed_it['Language'])))
            f.write("        <summary>{}</summary>\n".format(feed_it['Summary']))
            f.write("    </feed>\n")
        f.write("</root>\n")

def handle_settings(qd):
    c = get_cursor()

    s = ""

    # Write payload.
    s += "<!DOCTYPE html>\n"
    s += "<html>\n"
    s += "<head>\n"
    s += "<meta charset=\"UTF-8\">\n"
    s += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>\n"
    s += "<title>Settings</title>\n"
    s += "</head>\n"
    s += "<body>\n"
    s += "<h1>{}</h1>\n".format(qd['user'])

    # Display feeds.
    s += "<form>\n"
    for feed_it in c.execute("SELECT Feeds.*, Display.{} FROM Feeds INNER JOIN Display ON Feeds.ItemID=Display.ItemID ORDER BY Title COLLATE NOCASE".format(qd['user'])).fetchall():
        if feed_it[qd['user']] == 0:
            s += "<input type=\"checkbox\" name=\"{}\"><a href={}>{}</a>\n".format(feed_it['ItemID'], feed_it['Link'], feed_it['Title'])
        else:
            s += "<input type=\"checkbox\" name=\"{}\" checked><a href={}>{}</a>\n".format(feed_it['ItemID'], feed_it['Link'], feed_it['Title'])
        s += "{}\n".format(select_lang(feed_it['ItemID'], feed_it['Language']))
        s += "<br>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(qd['user'])
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/display_feeds.php\" value=\"Display feeds\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Add feed.
    s += "<form>\n"
    s += "<p>Title:<br>\n"
    s += "<input type=\"text\" name=\"title\"></p>\n"
    s += "<p>Link:<br>\n"
    s += "<input type=\"text\" name=\"link\"></p>\n"
    s += "<p>Display:<br>\n"
    s += "<input type=\"radio\" name=\"disp\" value=1 checked> Yes\n"
    s += "<input type=\"radio\" name=\"disp\" value=0> No\n"
    s += "</p>\n"
    s += "<p>Language:<br>\n"
    s += "{}\n".format(select_lang())
    s += "<p>Summary:<br>\n"
    s += "<input type=\"radio\" name=\"summary\" value=0> No abstract.\n"
    s += "<input type=\"radio\" name=\"summary\" value=1> First paragraph.\n"
    s += "<input type=\"radio\" name=\"summary\" value=2 checked> Full abstract.\n"
    s += "</p>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(qd['user'])
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/add_feed.php\" value=\"Add feed\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Delete feed.
    s += "<form>\n"
    s += "<p><select name=\"feed\">\n"
    for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title COLLATE NOCASE").fetchall():
        s += "<option value=\"{}\">{}</option>\n".format(feed_it['ItemID'], feed_it['Title'])
    s += "</select></p>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(qd['user'])
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/delete_feed.php\" value=\"Delete feed\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Load config.
    s += "<form>\n"
    s += "<p><input type=\"file\" name=\"feeds\" value=\"feeds\"></p>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(qd['user'])
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/load_config.php\" formenctype=\"multipart/form-data\" value=\"Load config\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Export config.
    s += "<form>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(qd['user'])
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/export_config.php\" value=\"Export config\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Add user.
    s += "<form>\n"
    s += "<p>Name:<br>\n"
    s += "<input type=\"text\" name=\"name\"></p>\n"
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/add_user.php\" value=\"Add user\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Rename user.
    s += "<form>\n"
    s += "<p>New name:<br>\n"
    s += "<input type=\"text\" name=\"name\"></p>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(qd['user'])
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/rename_user.php\" value=\"Rename user\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Delete user.
    s += "<form>\n"
    s += "<input type=\"hidden\" name=\"user\" value=\"{}\">\n".format(qd['user'])
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/delete_user.php\" value=\"Delete user\" style='background-color:red'></p>\n"
    s += "</form>\n"

    s += "</body>\n"
    s += "</html>\n"

    return s

def handle_statistics(user):
    c = get_cursor()

    s = ""

    # Write payload.
    s += "<!DOCTYPE html>\n"
    s += "<html>\n"
    s += "<head>\n"
    s += "<meta charset=\"UTF-8\">"
    s += "<title>Statistics</title>\n"
    s += "</head>\n"
    s += "<body>\n"

    # Likes.
    likes = c.execute("SELECT Items.*, Like.{0} FROM Items INNER JOIN Like ON Items.ItemID=Like.ItemID WHERE {0}=1 ORDER BY Published DESC".format(user, user)).fetchall()

    s += "<h2>Likes</h2>\n"
    s += "<p>{} likes.</p>\n".format(len(likes))
    s += "<ul>\n"
    for row_it in likes:
        datestamp = time.strftime("%A, %d %B %Y", time.strptime(row_it['Published'], "%Y-%m-%d %H:%M:%S GMT"))
        s += "<li>{}: <a href={}>{}</a> ({})</li>".format(row_it['Source'], row_it['Link'], row_it['Title'], datestamp)
    s += "</ul>\n"

    s += "<hr>\n"

    # Dislikes.
    dislikes = c.execute("SELECT Items.*, Like.{0} FROM Items INNER JOIN Like ON Items.ItemID=Like.ItemID WHERE {0}=-1 ORDER BY Published DESC".format(user, user)).fetchall()

    s += "<h2>Dislikes</h2>\n"
    s += "<p>{} dislikes.</p>\n".format(len(dislikes))
    s += "<ul>\n"
    for row_it in dislikes:
        datestamp = time.strftime("%A, %d %B %Y", time.strptime(row_it['Published'], "%Y-%m-%d %H:%M:%S GMT"))
        s += "<li>{}: <a href={}>{}</a> ({})</li>".format(row_it['Source'], row_it['Link'], row_it['Title'], datestamp)
    s += "</ul>\n"

    s += "</body>\n"
    s += "</html>\n"

    return s

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
            s = steins_generate_page(qd['user'], qd['lang'], qd['page'])
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
            handle_add_feed(qd)
            self.send_response(204)
            self.end_headers()

            self.path = "/settings.php"
            self.do_GET()
        # Delete feed.
        elif self.path == "/delete_feed.php":
            qlen = int(self.headers.get('content-length'))
            qs = self.rfile.read(qlen).decode('utf-8')
            qd = dict(parse_qsl(qs))
            handle_delete_feed(qd)
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
            handle_load_config(qd)
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
            handle_export_config(qd)
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
