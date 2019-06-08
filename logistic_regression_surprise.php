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

from steins_magic import handle_surprise
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_surprise(qd, 'Logistic Regression'))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
// system($bash_cmd . ' >> logistic_regression_surprise.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
