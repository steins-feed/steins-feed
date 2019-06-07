<?php
move_uploaded_file($_FILES["feeds"]["tmp_name"], "tmp_feeds.xml");
$python_cmd = <<<EOT
from steins_server import handle_load_config, handle_settings

handle_load_config()
print(handle_settings())
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\"";
// system($bash_cmd . ' >> load_config.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
