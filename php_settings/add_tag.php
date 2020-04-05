<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);
$db->exec("BEGIN");

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $_POST['user'], SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

$stmt = "INSERT INTO Tags (UserID, Name) VALUES (:UserID, :Name)";
$stmt = $db->prepare($stmt);
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
$stmt->bindValue(":Name", $_POST['tag'], SQLITE3_TEXT);
$res = $stmt->execute();

$db->exec("END");
$db->close();

$_GET = $_POST;
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/settings.php";
?>
