#!/usr/bin/env python3

import os
import subprocess
import sys
import time

from steins_feed import steins_update
from steins_server import steins_run, steins_halt
from steins_web import get_browser

dir_name = os.path.dirname(os.path.abspath(__file__))
db_name = dir_name + os.sep + "steins.db"
steins_update(db_name)

if "--no-gui" in sys.argv:
    sys.exit()

port = steins_run()
print("PORT: {}.".format(port))
#subprocess.run(["xdg-open", "http://localhost:{}/".format(port)])
#subprocess.run(["firefox", "-new-window", "http://localhost:{}/".format(port)])
browser = get_browser()
browser.get("http://localhost:{}/".format(port))

browser_open = True
while browser_open:
    try:
        browser.title
        time.sleep(5)
    except:
        browser_open = False

steins_halt()
