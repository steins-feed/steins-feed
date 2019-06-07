<?php
$python_cmd = <<<EOT
from steins_server import handle_statistics

print(handle_statistics())
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\"";
// system($bash_cmd . ' >> statistics.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
