<?php
if( !$_POST["user"] ) {
    $_POST["user"] = "nobody";
}
$post_query = http_build_query($_POST);
$python_cmd = <<<EOT
import sys

from steins_magic import handle_highlight
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_highlight(qd))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$post_query\"";
// system($bash_cmd . ' > highlight.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
