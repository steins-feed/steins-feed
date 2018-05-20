#!/usr/bin/env python3

import multiprocessing as mp
import os

from http.server import HTTPServer, BaseHTTPRequestHandler
from steins_feed import steins_update

class SteinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Generate page.
        if self.path == "/":
            steins_update()

        # Write header.
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        # Write payload.
        dir_name = os.path.dirname(os.path.abspath(__file__))
        if self.path == "/":
            f = open(dir_name+os.sep+"steins-0.html", 'r')
        else:
            f = open(dir_name+self.path, 'r')
        self.wfile.write(f.read().encode('utf-8'))
        f.close()

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
