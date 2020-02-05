<?php
function topnav($title) {
    echo '<div class="topnav">', PHP_EOL;
    echo '<h1>', PHP_EOL;
    echo $title, PHP_EOL;
    echo '<span class="scroll"></span>', PHP_EOL;
    echo '<span onclick="open_menu()" class="onclick">&#9776;&nbsp;</span>', PHP_EOL;
    echo '</h1>', PHP_EOL;
    echo '</div>', PHP_EOL;
}
?>
