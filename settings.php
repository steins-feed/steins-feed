<?php
$python_cmd = <<<EOT
from steins_server import handle_settings

print(handle_settings())
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\"";
// system($bash_cmd . ' >> settings.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
