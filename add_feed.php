<?php
$post_query = http_build_query($_POST);
$python_cmd = <<<EOT
import sys

from steins_server import handle_settings
from steins_sql import add_feed
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1], keep_blank_values=True))
add_feed(qd['title'], qd['link'], qd['disp'], qd['lang'], qd['summary'], qd['user'])
print(handle_settings(qd['user']))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$post_query\"";
// system($bash_cmd . ' > add_feed.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
