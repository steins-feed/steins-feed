<?php
if( !$_GET["user"] ) {
    $_GET["user"] = "nobody";
}
if( !$_GET["clf"] ) {
    $_GET["clf"] = "Naive Bayes";
}
$get_query = http_build_query($_GET);
$python_cmd = <<<EOT
import sys

from steins_magic import handle_analysis
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_analysis(qd['user'], qd['clf']))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
// system($bash_cmd . ' > analysis.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
