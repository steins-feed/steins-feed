#!/usr/bin/env python3

import sys
from steins_feed import steins_update

title_pattern = ""
if len(sys.argv) > 1:
    title_pattern = sys.argv[1]
steins_update(title_pattern)
