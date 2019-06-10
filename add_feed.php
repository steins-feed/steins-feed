<?php
if( !$_POST["user"] ) {
    $_POST["user"] = "nobody";
}
$post_query = http_build_query($_POST);
$python_cmd = <<<EOT
import sys

from steins_server import handle_add_feed, handle_settings
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1], keep_blank_values=True))
handle_add_feed(qd)
print(handle_settings(qd))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$post_query\"";
// system($bash_cmd . ' >> add_feed.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
