<?php
$post_query = http_build_query($_POST);
$python_cmd = <<<EOT
import sys

from steins_server import handle_like
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
handle_like(qd['user'], int(qd['id']), qd['submit'])
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$post_query\"";
// system($bash_cmd . ' >> like.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
