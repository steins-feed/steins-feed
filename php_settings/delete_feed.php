<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);

$stmt = "DELETE FROM Feeds WHERE FeedID=:FeedID";
$stmt = $db->prepare($stmt);
$stmt->bindValue(":FeedID", $_POST['feed'], SQLITE3_INTEGER);
$stmt->execute();

$db->close();
$_GET = $_POST;
include "../settings.php";
?>
