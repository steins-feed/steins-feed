#!/usr/bin/env python3

import os
import time

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs, parse_qsl
from xml.sax.saxutils import escape

from steins_config import add_feed, delete_feed, init_feeds
from steins_feed import steins_generate_page
from steins_magic import handle_naive_bayes, handle_logistic_regression
from steins_sql import get_connection, get_cursor

dir_path = os.path.dirname(os.path.abspath(__file__))

PORT = 8000

def handle_page(qd):
    return steins_generate_page(int(qd['page']))

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

def handle_settings():
    c = get_cursor()

    s = ""

    # Write payload.
    s += "<!DOCTYPE html>\n"
    s += "<html>\n"
    s += "<head>\n"
    s += "<meta charset=\"UTF-8\">"
    s += "<title>Settings</title>\n"
    s += "</head>\n"
    s += "<body>\n"

    # Display feeds.
    s += "<form>\n"
    for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title").fetchall():
        if feed_it[3] == 0:
            s += "<input type=\"checkbox\" name=\"{}\" value=\"{}\">{}<br>\n".format(feed_it[0], feed_it[1], feed_it[1])
        else:
            s += "<input type=\"checkbox\" name=\"{}\" value=\"{}\" checked>{}<br>\n".format(feed_it[0], feed_it[1], feed_it[1])
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/feeds\" value=\"Display feeds\"></p>\n"
    s += "</form>\n"

    s += "<hr>\n"

    # Add feed.
    s += "<form>\n"
    s += "<p>Title:<br>\n"
    s += "<input type=\"text\" name=\"title\"></p>\n"
    s += "<p>Link:<br>\n"
    s += "<input type=\"text\" name=\"link\"></p>\n"
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/add-feed\" value=\"Add feed\"></p>\n"
    s += "</form>\n"

    s += "<hr>\n"

    # Delete feed.
    s += "<form>\n"
    s += "<p><select name=\"feed\">\n"
    for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title").fetchall():
        s += "<option value=\"{}\">{}</option>\n".format(feed_it[0], feed_it[1])
    s += "</select></p>\n"
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/delete-feed\" value=\"Delete feed\"></p>\n"
    s += "</form>\n"

    s += "<hr>\n"

    # Load config.
    s += "<form>\n"
    s += "<p>File:<br>\n"
    s += "<input type=\"text\" name=\"file\"></p>\n"
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/load-config\" value=\"Load config\"></p>\n"
    s += "</form>\n"

    s += "<hr>\n"

    # Export config.
    s += "<form>\n"
    s += "<p>File:<br>\n"
    s += "<input type=\"text\" name=\"file\"></p>\n"
    s += "<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/export-config\" value=\"Export config\"></p>\n"
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
            s = handle_naive_bayes(qd)
            self.wfile.write(s.encode('utf-8'))
        elif "/logistic_regression.php" in self.path:
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            qs = urlsplit(self.path).query
            qd = dict(parse_qsl(qs))
            s = handle_logistic_regression(qd)
            self.wfile.write(s.encode('utf-8'))

    def do_POST(self):
        self.path = self.path.replace("/steins-feed", "")

        # Feeds.
        if self.path == "/feeds":
            conn = get_connection()
            c = conn.cursor()

            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = parse_qs(query.decode('utf-8'))
            query_keys = [int(q_it) for q_it in query_dict.keys()]

            for q_it in c.execute("SELECT * FROM Feeds").fetchall():
                if int(q_it[0]) in query_keys:
                    c.execute("UPDATE Feeds SET Display=1 WHERE ItemID=?", (q_it[0], ))
                else:
                    c.execute("UPDATE Feeds SET Display=0 WHERE ItemID=?", (q_it[0], ))
                conn.commit()

            self.path = "/"
            self.do_GET()
        # Add feed.
        elif "/add-feed" in self.path:
            conn = get_connection()
            c = conn.cursor()

            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = parse_qs(query)

            title = query_dict['title'.encode('utf-8')][0].decode('utf-8')
            link = query_dict['link'.encode('utf-8')][0].decode('utf-8')
            add_feed(title, link)

            conn.commit()
            self.settings_response()
        # Delete feed.
        elif "/delete-feed" in self.path:
            conn = get_connection()
            c = conn.cursor()

            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = parse_qs(query)

            item_id = int(query_dict['feed'.encode('utf-8')][0])
            row = c.execute("SELECT * FROM Feeds WHERE ItemID=?", (item_id, )).fetchone()
            delete_feed(row[1])

            conn.commit()
            self.settings_response()
        # Load config.
        elif "/load-config" in self.path:
            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = parse_qs(query)

            file_name = query_dict['file'.encode('utf-8')][0].decode('utf-8')
            file_path = dir_path + os.sep + file_name
            init_feeds(file_path)

            self.send_response(204)
            self.end_headers()
        # Export config.
        if "/export-config" in self.path:
            c = get_cursor()

            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = parse_qs(query)

            file_name = query_dict['file'.encode('utf-8')][0].decode('utf-8')
            file_path = dir_path + os.sep + file_name
            with open(file_path, 'w') as f:
                f.write("<?xml version=\"1.0\"?>\n")
                f.write("\n")
                f.write("<root>\n")
                for feed_it in c.execute("SELECT * FROM Feeds").fetchall():
                    f.write("    <feed>\n")
                    f.write("        <title>{}</title>\n".format(escape(feed_it[1])))
                    f.write("        <link>{}</link>\n".format(escape(feed_it[2])))
                    f.write("    </feed>\n")
                f.write("</root>\n")

            self.send_response(204)
            self.end_headers()
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
