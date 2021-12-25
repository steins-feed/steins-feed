import functools
import logging
import time
import typing

from . import Logger

def log_time(
    name: str,
) -> typing.Callable[[typing.Callable], typing.Callable]:
    logger = Logger(name, logging.INFO)

    def decorator(f: typing.Callable) -> typing.Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            tic = time.time()
            res = f(*args, **kwargs)
            toc = time.time()
            logger.info(f"Function {f.__name__} took {toc - tic} seconds.")
            return res

        return wrapper

    return decorator

