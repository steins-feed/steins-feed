<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 settings.py "' . http_build_query($_POST) . '" > settings.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 settings.py "' . http_build_query($_POST) . '"');
?>
