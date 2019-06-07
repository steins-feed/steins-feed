<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 add_feed.py "' . http_build_query($_POST) . '" >> add_feed.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 add_feed.py "' . http_build_query($_POST) . '"');
?>
