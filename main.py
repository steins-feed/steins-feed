#!/usr/bin/env python3

import subprocess

from steins_server import steins_run

port = steins_run()
#subprocess.run(["xdg-open", "http://localhost:{}/".format(port)])
subprocess.run(["firefox", "-new-window", "http://localhost:{}/".format(port)])
