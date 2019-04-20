#!/usr/bin/env python3

import sys

from steins_server import handle_like
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
like_mode = 1
if len(sys.argv) > 2:
    like_mode = int(sys.argv[2])
handle_like(qd, like_mode)
