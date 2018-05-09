#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler

class SteinsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        f = open("steins.html", 'r')
        self.wfile.write(f.read().encode('utf-8'))
        f.close()

try:
    server = HTTPServer(('localhost', 8000), SteinsHandler)
    server.serve_forever()
except KeyboardInterrupt:
    server.socket.close()
