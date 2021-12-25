#!/usr/bin/env python3

import os

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

