<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);
$db->exec("BEGIN");

$stmt = "INSERT INTO Users (Name) VALUES (:Name)";
$stmt = $db->prepare($stmt);
$stmt->bindValue(":Name", $_POST['name'], SQLITE3_TEXT);
$res = $stmt->execute();

if ($res) {
    $stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
    $stmt->bindValue(":Name", $_POST['name'], SQLITE3_TEXT);
    $res = $stmt->execute()->fetcharray();
    $user_id = $res['UserID'];

    $stmt = "INSERT INTO Display (UserID, FeedID) SELECT :UserID, FeedID FROM Feeds WHERE Language=:Language";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(":Language", $_POST['lang'], SQLITE3_TEXT);
    $stmt->execute();

    $_POST['user'] = $_POST['name'];
}

$db->exec("END");
$db->close();

$_GET = $_POST;
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/settings.php";
?>
