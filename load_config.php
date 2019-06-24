<?php
if( !$_GET["user"] ) {
    $_GET["user"] = "nobody";
}
$get_query = http_build_query($_GET);
$python_cmd = <<<EOT
import sys

from steins_server import handle_load_config, handle_settings
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1]))
handle_load_config(qd)
print(handle_settings(qd))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$get_query\"";
move_uploaded_file($_FILES["feeds"]["tmp_name"], "tmp_feeds.xml");
// system($bash_cmd . ' > load_config.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
