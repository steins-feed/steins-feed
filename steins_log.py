#!/usr/bin/env python3

import logging
import os

LOG_NAME = "steins.log"
dir_path = os.path.dirname(os.path.abspath(__file__))
log_path = dir_path + os.sep + LOG_NAME

def have_logger():
    if "logger" in globals():
        return True
    else:
        return False

def get_logger():
    global logger
    if not have_logger():
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

        fh = logging.FileHandler(log_path, encoding='utf-8')
        fh.setFormatter(formatter)

        logger = logging.getLogger('stein')
        logger.setLevel(logging.INFO)
        logger.addHandler(fh)
    return logger
