#!/usr/bin/env python3

import glob
import sys

from model.schema import create_schema
from model.feeds import read_feeds
from model.xml import read_xml

title_pattern = None
if len(sys.argv) > 1:
    title_pattern = sys.argv[1]

create_schema()
for file_it in glob.glob("feeds.d/*.xml"):
    with open(file_it, 'r') as f:
        read_xml(f)
read_feeds(title_pattern)
