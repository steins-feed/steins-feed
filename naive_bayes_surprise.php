<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 naive_bayes_surprise.py "' . http_build_query($_GET) . '" > naive_bayes_surprise.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 naive_bayes_surprise.py "' . http_build_query($_GET) . '"');
?>
