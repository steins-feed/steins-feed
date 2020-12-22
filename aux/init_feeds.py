#!/usr/bin/env python3

import glob

from model.schema import create_schema
from model.feeds import read_xml, read_feeds

create_schema()
for file_it in glob.glob("feeds.d/*.xml"):
    with open(file_it, 'r') as f:
        read_xml(f)
read_feeds()
