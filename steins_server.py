#!/usr/bin/env python3

import multiprocessing as mp
import os
import requests
import sqlite3

from http.server import HTTPServer, BaseHTTPRequestHandler
from lxml import html
from steins_feed import steins_update

dir_name = os.path.dirname(os.path.abspath(__file__))
db_name = dir_name + os.sep + "steins.db"

class SteinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generate page.
        if self.path == "/":
            steins_update(db_name)

        # Write header.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Write payload.
        dir_name = os.path.dirname(os.path.abspath(__file__))
        if self.path == "/":
            f = open(dir_name+os.sep+"steins-0.html", 'r')
        else:
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
        row = c.execute("SELECT * FROM Items WHERE ItemID=?", (self.path[1:], )).fetchone()

        # Load page.
        page = requests.get(row[5])
        tree = html.fromstring(page.content)

        if not row[4].find("WIRED") == -1:
            article = tree.xpath("//article")[0]
            article_body = article.xpath("./div")[0]
        if not row[4].find("The Guardian") == -1:
            article = tree.xpath("//article")[0]
            article_body = article.xpath(".//div[@itemprop='articleBody']")[0]
        if not row[4].find("The Atlantic") == -1:
            article = tree.xpath("//article")[0]
            article_sections = article.xpath(".//section")
            article_body = []
            for section_it in article_sections:
                for elem_it in section_it:
                    article_body.append(elem_it)

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
            can_print = False
            can_print |= (e_it.tag == "p")
            for i in range(6):
                can_print |= (e_it.tag == "h{}".format(i+1))
            can_print |= (e_it.tag == "blockquote")

            if can_print:
                self.wfile.write(html.tostring(e_it))
                self.wfile.write('\n'.encode('utf-8'))

        self.wfile.write("</body>\n".encode('utf-8'))

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
