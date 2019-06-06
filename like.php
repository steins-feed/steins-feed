<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 like.py "' . http_build_query($_POST) . '" > like.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 like.py "' . http_build_query($_POST) . '"');
?>
