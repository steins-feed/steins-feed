<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 statistics.py "' . http_build_query($_POST) . '" > statistics.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 statistics.py "' . http_build_query($_POST) . '"');
?>
