#!/usr/bin/env python3

import multiprocessing as mp
import os
import sqlite3

from http.server import HTTPServer, BaseHTTPRequestHandler
from steins_feed import steins_update
from steins_manager import get_handler

dir_name = os.path.dirname(os.path.abspath(__file__))
db_name = dir_name + os.sep + "steins.db"

class SteinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generate page.
        if self.path == "/":
            steins_update(db_name)
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

    def do_POST(self):
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        idx = self.path.find("/", 1)
        item_id = self.path[idx+1:]
        row = c.execute("SELECT * FROM Items WHERE ItemID=?", (item_id, )).fetchone()

        # Like.
        if "/like" in self.path:
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
            if row[6] == -1:
                c.execute("UPDATE Items SET Like=0 WHERE ItemID=?", (item_id, ))
                print("UNLIKE: {}.".format(row[1]))
            else:
                c.execute("UPDATE Items SET Like=-1 WHERE ItemID=?", (item_id, ))
                print("DISLIKE: {}.".format(row[1]))
            self.send_response(204)
            self.end_headers()
        # Print.
        else:
            self.print_response(row)
            print("PRINT: {}.".format(row[1]))

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
