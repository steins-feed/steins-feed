<?php
    if( !$_GET["page"] ) {
        $_GET["page"] = 0;
    }

    // system('env PYTHONIOENCODING=UTF-8 python3 index.py "' . http_build_query($_GET) . '" > index.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 index.py "' . http_build_query($_GET) . '"');
?>
