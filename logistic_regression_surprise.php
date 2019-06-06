<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 logistic_regression_surprise.py "' . http_build_query($_GET) . '" > logistic_regression_surprise.log 2>&1'); // DEBUG.
    system('env PYTHONIOENCODING=UTF-8 python3 logistic_regression_surprise.py "' . http_build_query($_GET) . '"');
?>
