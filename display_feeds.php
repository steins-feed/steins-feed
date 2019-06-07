<?php
$post_query = http_build_query($_POST);
$python_cmd = <<<EOT
import sys

from steins_server import handle_display_feeds, handle_page
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
handle_display_feeds(qd)
print(handle_page())
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$post_query\"";
// system($bash_cmd . ' >> display_feeds.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
