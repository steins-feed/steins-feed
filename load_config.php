<?php
    move_uploaded_file($_FILES["feeds"]["tmp_name"], "tmp_feeds.xml");
    // system('env PYTHONIOENCODING=UTF-8 python3 load_config.py >> load_config.log 2>&1'); // DEBUG
    system('env PYTHONIOENCODING=UTF-8 python3 load_config.py');
?>
