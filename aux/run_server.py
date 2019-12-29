#!/usr/bin/env python3

#import signal

from multiprocessing import Process
import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_server import steins_run
from steins_sql import close_connection

#sig_ign = signal.signal(signal.SIGINT, signal.SIG_IGN)
process = Process(target=steins_run)
#signal.signal(signal.SIGINT, sig_ign)
process.start()

try:
    process.join()
except KeyboardInterrupt:
    close_connection()
