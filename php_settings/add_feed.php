<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);
$db->exec("BEGIN");

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $_POST['user'], SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

$stmt = "INSERT INTO Feeds (Title, Link, Language, Summary) VALUES (:Title, :Link, :Language, :Summary)";
$stmt = $db->prepare($stmt);
$stmt->bindValue(":Title", $_POST['title'], SQLITE3_TEXT);
$stmt->bindValue(":Link", $_POST['link'], SQLITE3_TEXT);
$stmt->bindValue(":Language", $_POST['lang'], SQLITE3_TEXT);
$stmt->bindValue(":Summary", $_POST['summary'], SQLITE3_INTEGER);
$res = $stmt->execute();

if ($res) {
    $stmt = "SELECT FeedID FROM Feeds WHERE Title=:Title AND Link=:Link";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":Title", $_POST['title'], SQLITE3_TEXT);
    $stmt->bindValue(":Link", $_POST['link'], SQLITE3_TEXT);
    $res = $stmt->execute()->fetcharray();
    $feed_id = $res['FeedID'];

    $stmt = "INSERT INTO Display (UserID, FeedID) VALUES (:UserID, :FeedID)";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(":FeedID", $feed_id, SQLITE3_INTEGER);
    $stmt->execute();
}

$db->exec("END");
$db->close();

$_GET = $_POST;
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/settings.php";
?>
