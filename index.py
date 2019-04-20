#!/usr/bin/env python3

import sys

from steins_server import handle_page
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_page(qd))
