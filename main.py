#!/usr/bin/env python3

from steins import *

#from http.server import HTTPServer, BaseHTTPRequestHandler
#
#class SteinsServer(BaseHTTPRequestHandler):
#    def do_GET(self):
#        self.send_response(200)
#        self.send_header("Content-type", "text/html")
#        self.end_headers()

db_name = "steins.db"
db_exists = os.path.isfile(db_name)
conn = sqlite3.connect("steins.db")
c = conn.cursor()
if not db_exists:
    c.execute("CREATE TABLE Items (ItemID INT AUTO_INCREMENT, Title TEXT NOT NULL, Published DATETIME NOT NULL, Summary MEDIUMTEXT, Source TEXT NOT NULL, Link TEXT NOT NULL, PRIMARY KEY (ItemID))")
steins_read(c)
steins_write(c)
conn.commit()
conn.close()
