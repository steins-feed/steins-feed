<?php
if( !$_GET["page"] ) {
    $_GET["page"] = 0;
}
if( !$_GET["lang"] ) {
    $_GET["lang"] = "International";
}
$get_query = http_build_query($_GET);
$python_cmd = <<<EOT
import sys

from steins_server import handle_page
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_page(qd))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
// system($bash_cmd . ' >> index.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
