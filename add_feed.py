#!/usr/bin/env python3

import sys

from steins_server import handle_add_feed, handle_settings
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
handle_add_feed(qd)
print(handle_settings())
