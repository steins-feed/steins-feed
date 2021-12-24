#!/usr/bin/env python3

"""Interaction with file system."""

import datetime
import os

def is_up_to_date(file_path: str, datetime_ref: datetime.datetime) -> bool:
    """
    Checks whether file is more up to date than a given datetime.

    Args:
      file_path: File path.
      datetime_ref: Given datetime.
    """
    if not os.path.exists(file_path):
        return False

    file_timestamp = os.stat(file_path).st_mtime
    file_datetime = datetime.datetime.utcfromtimestamp(file_timestamp)
    return file_datetime > datetime_ref

def mkdir_p(dir_path: str):
    """
    Make directory if non-existent.

    Args:
      s: Absolute path of new directory.
    """
    try:
        os.mkdir(dir_path)
    except FileExistsError:
        pass

