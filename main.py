#!/usr/bin/env python3

import os
import subprocess

from steins_feed import steins_update
from steins_server import steins_run

dir_name = os.path.dirname(os.path.abspath(__file__))
db_name = dir_name + os.sep + "steins.db"
steins_update(db_name)

port = steins_run()
print("PORT: {}.".format(port))
#subprocess.run(["xdg-open", "http://localhost:{}/".format(port)])
subprocess.run(["firefox", "-new-window", "http://localhost:{}/".format(port)])
