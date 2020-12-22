#!/usr/bin/env python3

import logging
import os
import os.path as os_path

file_path = os_path.normpath(os_path.join(
        os_path.dirname(__file__),
        os.pardir,
        "steins.log"
))

formatter = None
handler = None

def get_formatter():
    global formatter
    if not formatter:
        formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s: %(message)s"
        )
    return formatter

def get_handler():
    global handler
    if not handler:
        handler = logging.FileHandler(file_path)
        handler.setFormatter(get_formatter())
    return handler
