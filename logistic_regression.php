<?php
if( !$_GET["user"] ) {
    $_GET["user"] = "nobody";
}
if( !$_GET["page"] ) {
    $_GET["page"] = 0;
}
if( !$_GET["lang"] ) {
    $_GET["lang"] = "International";
}
$get_query = http_build_query($_GET);
$python_cmd = <<<EOT
import sys

from steins_feed import steins_generate_page
from steins_magic import handle_magic
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
clf = handle_magic(qd, 'Logistic Regression')
print(steins_generate_page(qd['page'], qd['lang'], qd['user'], clf, -1))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
// system($bash_cmd . ' >> logistic_regression.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
