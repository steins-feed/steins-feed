import functools
import logging
import time

from . import Logger

def log_time(name):
    logger = Logger(name, logging.INFO)

    def log_time(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            tic = time.time()
            res = f(*args, **kwargs)
            toc = time.time()
            logger.info(f"Function {f.__name__} took {toc - tic} seconds.")
            return res

        return wrapper

    return log_time

