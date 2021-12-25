#!/usr/bin/env python3

import logging
from logging import handlers
import os
from util import io as util_io

class Formatter(logging.Formatter):
    instance = None

    def __new__(cls):
        if cls.instance:
            return cls.instance

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s:%(name)s: %(message)s"
        )

        cls.instance = formatter
        return formatter

class Handler(logging.Handler):
    instance = None

    dir_path = os.path.join(
        os.path.dirname(__file__),
        os.pardir,
        "log.d",
    )
    util_io.mkdir_p(dir_path)

    file_path = os.path.join(
        dir_path,
        "steins.log",
    )

    def __new__(cls):
        if cls.instance:
            return cls.instance

        #handler = logging.FileHandler(file_path)
        handler = handlers.TimedRotatingFileHandler(
            cls.file_path,
            when='midnight',
            backupCount=14,
        )

        formatter = Formatter()
        handler.setFormatter(formatter)

        cls.instance = handler
        return handler

class Logger(logging.Logger):
    instances = {}

    def __new__(cls, name="root", level=logging.WARNING):
        if name in cls.instances:
            return cls.instances[name]

        logger = logging.getLogger(name)
        logger.setLevel(level)

        handler = Handler()
        logger.addHandler(handler)

        cls.instances[name] = logger
        return logger

