<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 delete_feed.py "' . http_build_query($_POST) . '" >> delete_feed.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 delete_feed.py "' . http_build_query($_POST) . '"');
?>
