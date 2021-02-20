#!/usr/bin/env python3

import logging
from logging import handlers
import os

dir_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "log.d"
))
try:
    os.mkdir(dir_path)
except FileExistsError:
    pass
file_path = os.path.normpath(os.path.join(
        dir_path,
        "steins.log"
))

def get_formatter():
    global formatter
    if 'formatter' not in globals():
        formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s: %(message)s"
        )
    return formatter

def get_handler():
    global handler
    if 'handler' not in globals():
        #handler = logging.FileHandler(file_path)
        handler = handlers.TimedRotatingFileHandler(
                file_path,
                when='midnight',
                backupCount=14
        )
        handler.setFormatter(get_formatter())
    return handler
