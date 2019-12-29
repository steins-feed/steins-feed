#!/usr/bin/env python3

import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_xml import load_config

file_name = "feeds.xml"
if len(sys.argv) > 1:
    file_name = sys.argv[1]
file_path = dir_path + os.sep + file_name
load_config(file_path)
