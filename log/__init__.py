#!/usr/bin/env python3

import logging
import os

file_path = os.path.normpath(os.path.join(
        os.path.dirname(__file__),
        os.pardir,
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
        handler = logging.FileHandler(file_path)
        handler.setFormatter(get_formatter())
    return handler
