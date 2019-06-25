<?php
$post_query = http_build_query($_POST);
$python_cmd = <<<EOT
import sys

from steins_server import handle_settings
from steins_sql import delete_feed
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
delete_feed(int(qd['feed']), qd['user'])
print(handle_settings(qd['user'))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$post_query\"";
// system($bash_cmd . ' > delete_feed.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
