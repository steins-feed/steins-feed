<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 like.py ' . http_build_query($_POST) . ' -1' . ' > like.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 like.py ' . http_build_query($_POST) . ' -1');
?>
