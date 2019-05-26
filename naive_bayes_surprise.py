#!/usr/bin/env python3

import sys

from steins_magic import handle_surprise
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_surprise(qd))
