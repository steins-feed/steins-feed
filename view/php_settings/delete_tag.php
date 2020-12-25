<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);
$db->exec("BEGIN");

$stmt = "DELETE FROM Tags WHERE TagID=:TagID";
$stmt = $db->prepare($stmt);
$stmt->bindValue(":TagID", $_POST['tag'], SQLITE3_INTEGER);
$stmt->execute();

$db->exec("END");
$db->close();

$_GET = $_POST;
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/settings.php";
?>
