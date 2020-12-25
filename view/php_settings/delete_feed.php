<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);
$db->exec("BEGIN");

$stmt = "DELETE FROM Feeds WHERE FeedID=:FeedID";
$stmt = $db->prepare($stmt);
$stmt->bindValue(":FeedID", $_POST['feed'], SQLITE3_INTEGER);
$stmt->execute();

$db->exec("END");
$db->close();

$_GET = $_POST;
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/settings.php";
?>
