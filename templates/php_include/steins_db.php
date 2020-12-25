<?php
function steins_db($flags = null) {
    if ($flags) {
        $db = new SQLite3($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/steins.db");
    } else {
        $db = new SQLite3($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/steins.db", $flags);
    }
    $db->exec("PRAGMA foreign_keys=ON");
    return $db;
}
?>
