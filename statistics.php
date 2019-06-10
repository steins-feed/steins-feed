<?php
if( !$_GET["user"] ) {
    $_GET["user"] = "nobody";
}
$python_cmd = <<<EOT
import sys

from steins_server import handle_statistics
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_statistics(qd))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
// system($bash_cmd . ' >> statistics.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
