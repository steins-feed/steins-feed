<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);

$stmt = "DELETE FROM Tags WHERE TagID=:TagID";
$stmt = $db->prepare($stmt);
$stmt->bindValue(":TagID", $_POST['tag'], SQLITE3_INTEGER);
$stmt->execute();

$db->close();
$_GET = $_POST;
include "../settings.php";
?>
