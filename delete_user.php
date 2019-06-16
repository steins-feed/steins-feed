<?php
$post_query = http_build_query($_POST);
$python_cmd = <<<EOT
import sys

from steins_server import delete_user, handle_page
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
delete_user(qd['user'])
print(handle_page({'user': "nobody"}))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$post_query\"";
// system($bash_cmd . ' >> add_feed.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
