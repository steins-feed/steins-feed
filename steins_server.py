#!/usr/bin/env python3

import os

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, parse_qs, parse_qsl
from xml.sax.saxutils import escape

from steins_config import add_feed, delete_feed, init_feeds
from steins_feed import steins_write_body
from steins_sql import get_connection, get_cursor

dir_path = os.path.dirname(os.path.abspath(__file__))

PORT = 8000

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
            qs = urlsplit(self.path).query
            qs = dict(parse_qsl(qs))
            self.page_response(int(qs['page']))
        elif self.path == "/favicon.ico":
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()

            file_path = dir_path + os.sep + self.path
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == "/settings.php":
            self.settings_response()

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
        elif "/like" in self.path:
            conn = get_connection()
            c = conn.cursor()

            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = dict(parse_qsl(query))

            item_id = int(query_dict['id'.encode('utf-8')])
            row = c.execute("SELECT * FROM Items WHERE ItemID=?", (item_id, )).fetchone()
            if row[6] == 1:
                c.execute("UPDATE Items SET Like=0 WHERE ItemID=?", (item_id, ))
                print("UNLIKE: {}.".format(row[1]))
            else:
                c.execute("UPDATE Items SET Like=1 WHERE ItemID=?", (item_id, ))
                print("LIKE: {}.".format(row[1]))

            conn.commit()
            self.send_response(204)
            self.end_headers()
        # Dislike.
        elif "/dislike" in self.path:
            conn = get_connection()
            c = conn.cursor()

            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = dict(parse_qsl(query))

            item_id = int(query_dict['id'.encode('utf-8')])
            row = c.execute("SELECT * FROM Items WHERE ItemID=?", (item_id, )).fetchone()
            if row[6] == -1:
                c.execute("UPDATE Items SET Like=0 WHERE ItemID=?", (item_id, ))
                print("UNLIKE: {}.".format(row[1]))
            else:
                c.execute("UPDATE Items SET Like=-1 WHERE ItemID=?", (item_id, ))
                print("DISLIKE: {}.".format(row[1]))

            conn.commit()
            self.send_response(204)
            self.end_headers()

    def page_response(self, page_no):
        # Write header.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Write payload.
        self.wfile.write("<!DOCTYPE html>\n".encode('utf-8'))
        self.wfile.write("<html>\n".encode('utf-8'))
        self.wfile.write("<head>\n".encode('utf-8'))
        self.wfile.write("<meta charset=\"UTF-8\">".encode('utf-8'))
        self.wfile.write("<title>Stein's Feed</title>\n".encode('utf-8'))
        self.wfile.write("</head>\n".encode('utf-8'))
        self.wfile.write("<body>\n".encode('utf-8'))
        self.wfile.write(steins_write_body(page_no).encode('utf-8'))
        self.wfile.write("</body>\n".encode('utf-8'))
        self.wfile.write("</html>\n".encode('utf-8'))

    def settings_response(self):
        c = get_cursor()

        # Write header.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Write payload.
        self.wfile.write("<!DOCTYPE html>\n".encode('utf-8'))
        self.wfile.write("<html>\n".encode('utf-8'))
        self.wfile.write("<head>\n".encode('utf-8'))
        self.wfile.write("<meta charset=\"UTF-8\">".encode('utf-8'))
        self.wfile.write("<title>Settings</title>\n".encode('utf-8'))
        self.wfile.write("</head>\n".encode('utf-8'))
        self.wfile.write("<body>\n".encode('utf-8'))

        # Display feeds.
        self.wfile.write("<form>\n".encode('utf-8'))
        for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title").fetchall():
            if feed_it[3] == 0:
                self.wfile.write("<input type=\"checkbox\" name=\"{}\" value=\"{}\">{}<br>\n".format(feed_it[0], feed_it[1], feed_it[1]).encode('utf-8'))
            else:
                self.wfile.write("<input type=\"checkbox\" name=\"{}\" value=\"{}\" checked>{}<br>\n".format(feed_it[0], feed_it[1], feed_it[1]).encode('utf-8'))
        self.wfile.write("<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/feeds\" value=\"Display feeds\"></p>\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("<hr>\n".encode('utf-8'))

        # Add feed.
        self.wfile.write("<form>\n".encode('utf-8'))
        self.wfile.write("<p>Title:<br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"text\" name=\"title\"></p>\n".encode('utf-8'))
        self.wfile.write("<p>Link:<br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"text\" name=\"link\"></p>\n".encode('utf-8'))
        self.wfile.write("<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/add-feed\" value=\"Add feed\"></p>\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("<hr>\n".encode('utf-8'))

        # Delete feed.
        self.wfile.write("<form>\n".encode('utf-8'))
        self.wfile.write("<p><select name=\"feed\">\n".encode('utf-8'))
        for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title").fetchall():
            self.wfile.write("<option value=\"{}\">{}</option>\n".format(feed_it[0], feed_it[1]).encode('utf-8'))
        self.wfile.write("</select></p>\n".encode('utf-8'))
        self.wfile.write("<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/delete-feed\" value=\"Delete feed\"></p>\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("<hr>\n".encode('utf-8'))

        # Load config.
        self.wfile.write("<form>\n".encode('utf-8'))
        self.wfile.write("<p>File:<br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"text\" name=\"file\"></p>\n".encode('utf-8'))
        self.wfile.write("<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/load-config\" value=\"Load config\"></p>\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("<hr>\n".encode('utf-8'))

        # Export config.
        self.wfile.write("<form>\n".encode('utf-8'))
        self.wfile.write("<p>File:<br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"text\" name=\"file\"></p>\n".encode('utf-8'))
        self.wfile.write("<p><input type=\"submit\" formmethod=\"post\" formaction=\"/steins-feed/export-config\" value=\"Export config\"></p>\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("</body>\n".encode('utf-8'))
        self.wfile.write("</html>\n".encode('utf-8'))

def steins_run():
    global PORT
    port = PORT

    while True:
        try:
            server = HTTPServer(('localhost', port), SteinsHandler)
            break
        except OSError:
            port += 2

    print("Connection open: {}.".format(port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
    print("Connection closed.")

    PORT = port

if __name__ == "__main__":
    from steins_sql import close_connection

    steins_run()
    close_connection()
