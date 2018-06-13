#!/usr/bin/env python3

import multiprocessing as mp
import os
import sqlite3
import urllib

from http.server import HTTPServer, BaseHTTPRequestHandler
from steins_config import *
from steins_feed import steins_update
from steins_manager import get_handler
from xml.sax.saxutils import escape

dir_name = os.path.dirname(os.path.abspath(__file__))
db_name = dir_name + os.sep + "steins.db"

class SteinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generate page.
        if self.path == "/":
            #steins_update(db_name)
            self.path += "steins-0.html"
            self.do_GET()
            return

        if self.path == "/favicon.ico":
            # Write header.
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()

            f = open(dir_name+self.path, 'rb')
            self.wfile.write(f.read())
            f.close()
            return

        if self.path == "/settings":
            self.settings_response()
            return

        # Write header.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Write payload.
        try:
            f = open(dir_name+self.path, 'r')
        except FileNotFoundError as e:
            print("'{}' not found.".format(e.filename))
            return
        self.wfile.write(f.read().encode('utf-8'))
        f.close()

    def do_POST(self):
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        # Like.
        if "/like" in self.path:
            idx = self.path.find("/", 1)
            item_id = self.path[idx+1:]
            row = c.execute("SELECT * FROM Items WHERE ItemID=?", (item_id, )).fetchone()
            if row[6] == 1:
                c.execute("UPDATE Items SET Like=0 WHERE ItemID=?", (item_id, ))
                print("UNLIKE: {}.".format(row[1]))
            else:
                c.execute("UPDATE Items SET Like=1 WHERE ItemID=?", (item_id, ))
                print("LIKE: {}.".format(row[1]))
            self.send_response(204)
            self.end_headers()
        # Dislike.
        elif "/dislike" in self.path:
            idx = self.path.find("/", 1)
            item_id = self.path[idx+1:]
            row = c.execute("SELECT * FROM Items WHERE ItemID=?", (item_id, )).fetchone()
            if row[6] == -1:
                c.execute("UPDATE Items SET Like=0 WHERE ItemID=?", (item_id, ))
                print("UNLIKE: {}.".format(row[1]))
            else:
                c.execute("UPDATE Items SET Like=-1 WHERE ItemID=?", (item_id, ))
                print("DISLIKE: {}.".format(row[1]))
            self.send_response(204)
            self.end_headers()
        # Settings.
        elif self.path == "/":
            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = urllib.parse.parse_qs(query)
            query_keys = [int(q_it) for q_it in query_dict.keys()]

            for q_it in c.execute("SELECT * FROM Feeds").fetchall():
                if int(q_it[0]) in query_keys:
                    c.execute("UPDATE Feeds SET Display=1 WHERE ItemID=?", (q_it[0], ))
                else:
                    c.execute("UPDATE Feeds SET Display=0 WHERE ItemID=?", (q_it[0], ))

            conn.commit()
            conn.close()
            self.do_GET()
            return
        # Add feed.
        elif "/add-feed" in self.path:
            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = urllib.parse.parse_qs(query)

            title = query_dict['title'.encode('utf-8')][0].decode('utf-8')
            link = query_dict['link'.encode('utf-8')][0].decode('utf-8')
            add_feed(c, title, link)

            conn.commit()
            conn.close()
            self.settings_response()
            return
        # Delete feed.
        elif "/delete-feed" in self.path:
            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = urllib.parse.parse_qs(query)

            item_id = int(query_dict['feed'.encode('utf-8')][0])
            row = c.execute("SELECT * FROM Feeds WHERE ItemID=?", (item_id, )).fetchone()
            delete_feed(c, row[1])

            conn.commit()
            conn.close()
            self.settings_response()
            return
        # Load config.
        elif "/load-config" in self.path:
            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = urllib.parse.parse_qs(query)

            filename = query_dict['file'.encode('utf-8')][0].decode('utf-8')
            init_feeds(c, filename)

            conn.commit()
            conn.close()
            self.settings_response()
            return
        # Export config.
        elif "/export-config" in self.path:
            query_len = int(self.headers.get('content-length'))
            query = self.rfile.read(query_len)
            query_dict = urllib.parse.parse_qs(query)

            filename = query_dict['file'.encode('utf-8')][0].decode('utf-8')
            f = open(dir_name+os.sep+filename, 'w')
            f.write("<?xml version=\"1.0\"?>\n")
            f.write("\n")
            f.write("<root>\n")
            for feed_it in c.execute("SELECT * FROM Feeds").fetchall():
                f.write("    <feed>\n")
                f.write("        <title>{}</title>\n".format(escape(feed_it[1])))
                f.write("        <link>{}</link>\n".format(escape(feed_it[2])))
                f.write("    </feed>\n")
            f.write("</root>\n")
            f.close()

            self.send_response(204)
            self.end_headers()
        # Print.
        else:
            idx = self.path.find("/", 1)
            item_id = self.path[idx+1:]
            row = c.execute("SELECT * FROM Items WHERE ItemID=?", (item_id, )).fetchone()
            self.print_response(row)
            print("PRINT: {}.".format(row[1]))

        conn.commit()
        conn.close()

    def print_response(self, row):
        # Load page.
        handler = get_handler(row[4])
        article_body = handler.get_article_body(row[5])

        # Write header.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Write payload.
        self.wfile.write("<!DOCTYPE html>\n".encode('utf-8'))
        self.wfile.write("<html>\n".encode('utf-8'))
        self.wfile.write("<head>\n".encode('utf-8'))
        self.wfile.write("<meta charset=\"UTF-8\">".encode('utf-8'))
        self.wfile.write("<title>{}</title>\n".format(row[1]).encode('utf-8'))
        self.wfile.write("</head>\n".encode('utf-8'))
        self.wfile.write("<body>\n".encode('utf-8'))
        self.wfile.write("<h1>{}</h1>\n".format(row[1]).encode('utf-8'))
        self.wfile.write("<p>Source: {}. Published: {}</p>".format(row[4], row[2]).encode('utf-8'))
        for e_it in article_body:
            self.wfile.write(e_it + '\n'.encode('utf-8'))
        self.wfile.write("</body>\n".encode('utf-8'))
        self.wfile.write("</html>\n".encode('utf-8'))

    def settings_response(self):
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

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
        self.wfile.write("<p><input type=\"submit\" formmethod=\"post\" formaction=\"/\" value=\"Display feeds\"></p>\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("<hr>\n".encode('utf-8'))

        # Add feed.
        self.wfile.write("<form>\n".encode('utf-8'))
        self.wfile.write("Title:<br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"text\" name=\"title\"><br><br>\n".encode('utf-8'))
        self.wfile.write("Link:<br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"text\" name=\"link\"><br><br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"submit\" formmethod=\"post\" formaction=\"/add-feed\" value=\"Add feed\">\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("<hr>\n".encode('utf-8'))

        # Delete feed.
        self.wfile.write("<form>\n".encode('utf-8'))
        self.wfile.write("<p><select name=\"feed\">\n".encode('utf-8'))
        for feed_it in c.execute("SELECT * FROM Feeds ORDER BY Title").fetchall():
            self.wfile.write("<option value=\"{}\">{}</option>\n".format(feed_it[0], feed_it[1]).encode('utf-8'))
        self.wfile.write("</select></p>\n".encode('utf-8'))
        self.wfile.write("<p><input type=\"submit\" formmethod=\"post\" formaction=\"/delete-feed\" value=\"Delete feed\"></p>\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("<hr>\n".encode('utf-8'))

        # Load config.
        self.wfile.write("<form>\n".encode('utf-8'))
        self.wfile.write("File:<br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"text\" name=\"file\"><br><br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"submit\" formmethod=\"post\" formaction=\"/load-config\" value=\"Load config\">\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("<hr>\n".encode('utf-8'))

        # Export config.
        self.wfile.write("<form>\n".encode('utf-8'))
        self.wfile.write("File:<br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"text\" name=\"file\"><br><br>\n".encode('utf-8'))
        self.wfile.write("<input type=\"submit\" formmethod=\"post\" formaction=\"/export-config\" value=\"Export config\">\n".encode('utf-8'))
        self.wfile.write("</form>\n".encode('utf-8'))

        self.wfile.write("</body>\n".encode('utf-8'))
        self.wfile.write("</html>\n".encode('utf-8'))

        conn.commit()
        conn.close()

def steins_run_child(server):
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()
        print("Connection closed.")

def steins_run():
    PORT = 8000

    while True:
        try:
            server = HTTPServer(('localhost', PORT), SteinsHandler)
            print("Connection open.")
            break
        except OSError:
            PORT += 2

    p = mp.Process(target=steins_run_child, args=(server, ))
    p.start()

    return PORT
