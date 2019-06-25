<?php
$get_query = http_build_query($_GET);
$python_cmd = <<<EOT
import sys

from steins_server import handle_export_config
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
handle_export_config(qd['user'])
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
// system($bash_cmd . ' >> export_config.log 2>&1'); // DEBUG.
system($bash_cmd);
header("Content-Description: File Transfer");
header("Content-Type: application/xml");
header("Content-Disposition: attachment; filename=tmp_feeds.xml");
readfile("tmp_feeds.xml");
?>
