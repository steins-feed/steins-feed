<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 display_feeds.py "' . http_build_query($_POST) . '" >> display_feeds.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 display_feeds.py "' . http_build_query($_POST) . '"');
?>
