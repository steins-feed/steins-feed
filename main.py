#!/usr/bin/env python3

import os.path
import subprocess

subprocess.Popen(["python3", "steins_server.py"])
subprocess.Popen(["python3", "steins_feed.py"])
while not os.path.isfile("steins.html"):
    pass
subprocess.run(["xdg-open", "http://localhost:8000/"])
