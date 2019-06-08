#!/usr/bin/env python3

import os
import time

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs, parse_qsl
from xml.sax.saxutils import escape

from steins_feed import steins_generate_page
from steins_html import select_lang
from steins_magic import handle_magic, handle_surprise
from steins_sql import get_connection, get_cursor, add_feed, delete_feed, init_feeds

dir_path = os.path.dirname(os.path.abspath(__file__))

PORT = 8000

def handle_page(qd={'page': "0", 'lang': "International"}):
    return steins_generate_page(int(qd['page']), qd['lang'])

def handle_like(qd, val=1):
    conn = get_connection()
    c = conn.cursor()

    item_id = int(qd['id'])
    row = c.execute("SELECT * FROM Items WHERE ItemID=?", (item_id, )).fetchone()
    if row[6] == val:
        c.execute("UPDATE Items SET Like=0 WHERE ItemID=?", (item_id, ))
    else:
        c.execute("UPDATE Items SET Like=? WHERE ItemID=?", (val, item_id, ))

    conn.commit()

def handle_display_feeds(qd):
    conn = get_connection()
    c = conn.cursor()

    for q_it in c.execute("SELECT * FROM Feeds").fetchall():
        if str(q_it[0]) in qd.keys():
            c.execute("UPDATE Feeds SET Display=1 WHERE ItemID=?", (q_it[0], ))
        else:
            c.execute("UPDATE Feeds SET Display=0 WHERE ItemID=?", (q_it[0], ))

        c.execute("UPDATE Feeds SET Language=? WHERE ItemID=?", (qd["lang_{}".format(q_it[0])], q_it[0]))

        conn.commit()

def handle_add_feed(qd):
    title = qd['title']
    link = qd['link']
    disp = qd['disp']
    lang = qd['lang']
    summary = qd['summary']
    add_feed(title, link, disp, lang, summary)

def handle_delete_feed(qd):
    item_id = int(qd['feed'])
    delete_feed(item_id)

def handle_load_config():
    init_feeds(dir_path + os.sep + "tmp_feeds.xml")

def handle_export_config():
    c = get_cursor()
    feeds = c.execute("SELECT * FROM Feeds").fetchall()

    with open("tmp_feeds.xml", 'w', encoding='utf-8') as f:
        f.write("<?xml version=\"1.0\"?>\n\n")
        f.write("<root>\n")
        for feed_it in feeds:
            f.write("    <feed>\n")
            f.write("        <title>{}</title>\n".format(escape(feed_it[1])))
            f.write("        <link>{}</link>\n".format(escape(feed_it[2])))
            f.write("    </feed>\n")
        f.write("</root>\n")

def handle_settings():
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

    # Display feeds.
    s += "<form>\n"
    for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title").fetchall():
        if feed_it[3] == 0:
            s += "<input type=\"checkbox\" name=\"{}\">{}\n".format(feed_it[0], feed_it[1])
        else:
            s += "<input type=\"checkbox\" name=\"{}\" checked>{}\n".format(feed_it[0], feed_it[1])
        s += "{}\n".format(select_lang(feed_it[0], feed_it[4]))
        s += "<br>\n"
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
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/add_feed.php\" value=\"Add feed\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Delete feed.
    s += "<form>\n"
    s += "<p><select name=\"feed\">\n"
    for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title").fetchall():
        s += "<option value=\"{}\">{}</option>\n".format(feed_it[0], feed_it[1])
    s += "</select></p>\n"
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/delete_feed.php\" value=\"Delete feed\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Load config.
    s += "<form>\n"
    s += "<p><input type=\"file\" name=\"feeds\" value=\"feeds\"></p>\n"
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/load_config.php\" formenctype=\"multipart/form-data\" value=\"Load config\"></p>\n"
    s += "</form>\n"
    s += "<hr>\n"

    # Export config.
    s += "<form>\n"
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/export_config.php\" value=\"Export config\"></p>\n"
    s += "</form>\n"

    s += "</body>\n"
    s += "</html>\n"

    return s

def handle_statistics():
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
    likes = c.execute("SELECT * FROM Items WHERE Like=1 ORDER BY Published DESC").fetchall()

    s += "<h2>Likes</h2>\n"
    s += "<p>{} likes.</p>\n".format(len(likes))
    s += "<ul>\n"
    for row_it in likes:
        datestamp = time.strftime("%A, %d %B %Y", time.strptime(row_it[2], "%Y-%m-%d %H:%M:%S GMT"))
        s += "<li>{}: <a href={}>{}</a> ({})</li>".format(row_it[4], row_it[5], row_it[1], datestamp)
    s += "</ul>\n"

    s += "<hr>\n"

    # Dislikes.
    likes = c.execute("SELECT * FROM Items WHERE Like=-1 ORDER BY Published DESC").fetchall()

    s += "<h2>Dislikes</h2>\n"
    s += "<p>{} dislikes.</p>\n".format(len(likes))
    s += "<ul>\n"
    for row_it in likes:
        datestamp = time.strftime("%A, %d %B %Y", time.strptime(row_it[2], "%Y-%m-%d %H:%M:%S GMT"))
        s += "<li>{}: <a href={}>{}</a> ({})</li>".format(row_it[4], row_it[5], row_it[1], datestamp)
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
            s = handle_page(qd)
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

            s = handle_settings()
            self.wfile.write(s.encode('utf-8'))
        elif self.path == "/statistics.php":
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            s = handle_statistics()
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
            s = handle_surprise(qd)
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
            s = handle_surprise(qd, 'Logistic Regression')
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
            handle_load_config()
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

            handle_export_config()
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
