#!/usr/bin/env python3

import subprocess
import sys
import time

from steins_feed import steins_update
from steins_server import steins_run, steins_halt
from steins_web import get_browser

#subprocess.run(["xdg-open", "http://localhost:{}/".format(port)])
#subprocess.run(["firefox", "-new-window", "http://localhost:{}/".format(port)])
browser = get_browser(interaction_mode=True)

steins_update()
port = steins_run()
browser.get("http://localhost:{}/".format(port))

browser_open = True
while browser_open:
    try:
        browser.title
        time.sleep(5)
    except:
        browser_open = False

steins_halt()
