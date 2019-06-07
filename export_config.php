<?php
$python_cmd = <<<EOT
from steins_server import handle_export_config

handle_export_config()
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\"";
// system($bash_cmd . ' >> export_config.log 2>&1'); // DEBUG.
system($bash_cmd);
header("Content-Description: File Transfer");
header("Content-Type: application/xml");
header("Content-Disposition: attachment; filename=tmp_feeds.xml");
readfile("tmp_feeds.xml");
?>
