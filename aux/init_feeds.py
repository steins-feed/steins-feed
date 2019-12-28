#!/usr/bin/env python3

import os
import sys

from steins_xml import load_config

dir_path = os.getcwd()
file_name = "feeds.xml"
if len(sys.argv) > 1:
    file_name = sys.argv[1]
file_path = dir_path + os.sep + file_name
load_config(file_path)
#import cProfile
#cProfile.run("load_config(file_path)")
