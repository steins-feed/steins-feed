<?php
if( !$_POST["page"] ) {
    $_POST["page"] = 0;
}
if( !$_POST["lang"] ) {
    $_POST["lang"] = "International";
}
if( !$_POST["user"] ) {
    $_POST["user"] = "nobody";
}
$post_query = http_build_query($_POST);
$python_cmd = <<<EOT
import sys

from steins_feed import steins_generate_page
from steins_server import handle_display_feeds
from urllib.parse import parse_qsl

qd = dict(parse_qsl(sys.argv[1], keep_blank_values=True))
handle_display_feeds(qd)
print(steins_generate_page(qd['user'], qd['lang'], int(qd['page'])))
EOT;
$bash_cmd = "env PYTHONIOENCODING=UTF-8 python3 -c \"$python_cmd\" \"$post_query\"";
// system($bash_cmd . ' > display_feeds.log 2>&1'); // DEBUG.
system($bash_cmd);
?>
