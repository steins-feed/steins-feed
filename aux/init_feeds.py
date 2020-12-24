#!/usr/bin/env python3

import glob

from model.schema import create_schema
from model.xml import read_xml

create_schema()
for file_it in glob.glob("feeds.d/*.xml"):
    with open(file_it, 'r') as f:
        read_xml(f)
