#!/usr/bin/env python3

import sys

from steins_magic import handle_logistic_regression
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_logistic_regression(qd, surprise=10))
