#!/usr/bin/env python3

#import signal
#import subprocess

from multiprocessing import Process

from steins_feed import steins_update
from steins_server import steins_run, PORT
from steins_sql import close_connection
from steins_web import close_browser, get_browser

#subprocess.run(["xdg-open", "http://localhost:{}/".format(port)])
#subprocess.run(["firefox", "-new-window", "http://localhost:{}/".format(port)])
browser = get_browser(interaction_mode=True)

steins_update(read_mode=False)
#sig_ign = signal.signal(signal.SIGINT, signal.SIG_IGN)
process = Process(target=steins_run)
#signal.signal(signal.SIGINT, sig_ign)
process.start()
browser.get("http://localhost:{}/".format(PORT))
try:
    process.join()
except KeyboardInterrupt:
    close_connection()
    close_browser()
