#!/usr/bin/env python3

from datetime import datetime
import os

def is_up_to_date(file_path: str, datetime_ref: datetime) -> bool:
    if not os.path.exists(file_path):
        return False

    file_timestamp = os.stat(file_path).st_mtime
    file_datetime = datetime.utcfromtimestamp(file_timestamp)
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

