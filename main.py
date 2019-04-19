#!/usr/bin/env python3

import os
import subprocess
import sys
import time

from steins_feed import steins_update
from steins_server import steins_run, steins_halt
from steins_web import get_browser, close_browser

steins_update(not "--no-read" in sys.argv, not "--no-write" in sys.argv)

if "--no-gui" in sys.argv:
    close_browser()
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
