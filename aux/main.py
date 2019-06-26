#!/usr/bin/env python3

#import signal

from multiprocessing import Process

from steins_feed import steins_update
from steins_server import steins_run
from steins_sql import close_connection

#sig_ign = signal.signal(signal.SIGINT, signal.SIG_IGN)
process = Process(target=steins_run)
#signal.signal(signal.SIGINT, sig_ign)
process.start()

steins_update()

try:
    process.join()
except KeyboardInterrupt:
    close_connection()
