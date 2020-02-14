#!/usr/bin/env python3

import json
import os
import sys

dir_path = os.path.abspath(__file__)
dir_path = os.path.dirname(dir_path)
dir_path = os.path.join(dir_path, '..')
dir_path = os.path.abspath(dir_path)

sys.path.append(dir_path)

from steins_magic import steins_predict
from steins_sql import close_connection

user_id = sys.argv[1]
classifier = sys.argv[2]
items = json.loads(sys.argv[3])

res = steins_predict(user_id, classifier, items)
print(json.dumps(res))

close_connection()
