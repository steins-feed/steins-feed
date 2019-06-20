<?php
if( !$_GET["user"] ) {
    $_GET["user"] = "nobody";
}
if( !$_GET["lang"] ) {
    $_GET["lang"] = "International";
}
if( !$_GET["page"] ) {
    $_GET["page"] = "0";
}
if( !$_GET["feed"] ) {
    $_GET["feed"] = "Full";
}
if( !$_GET["clf"] ) {
    $_GET["clf"] = "Naive Bayes";
}
$get_query = http_build_query($_GET);
$python_cmd = <<<EOT
import sys

from steins_feed import steins_generate_page
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(steins_generate_page(qd['user'], qd['lang'], int(qd['page']), qd['feed'], qd['clf']))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
// system($bash_cmd . ' > index.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
