<?php
    // system('env PYTHONIOENCODING=UTF-8 python3 export_config.py >> export_config.log 2>&1'); // DEBUG
    system('env PYTHONIOENCODING=UTF-8 python3 export_config.py');
    header("Content-Description: File Transfer");
    header("Content-Type: application/xml");
    header("Content-Disposition: attachment; filename=tmp_feeds.xml");
    readfile("tmp_feeds.xml");
?>
