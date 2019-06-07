<?php
$get_query = http_build_query($_GET);
$python_cmd = <<<EOT
import sys

from steins_magic import handle_magic
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
print(handle_magic(qd, 'Logistic Regression'))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
// system($bash_cmd . ' >> logistic_regression.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
