<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $_POST['user'], SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

$feeds = simplexml_load_file($_FILES["feeds"]["tmp_name"]);

foreach ($feeds->feed as $feed_it) {
    $title = $feed_it->title;
    $link = $feed_it->link;
    $lang = $feed_it->lang;
    $summary = $feed_it->summary;

    if ($title and $link and $lang and $summary) {
        $stmt = "INSERT INTO Feeds (Title, Link, Language, Summary) VALUES (:Title, :Link, :Language, :Summary)";
        $stmt = $db->prepare($stmt);
        $stmt->bindValue(":Title", $title, SQLITE3_TEXT);
        $stmt->bindValue(":Link", $link, SQLITE3_TEXT);
        $stmt->bindValue(":Language", $lang, SQLITE3_TEXT);
        $stmt->bindValue(":Summary", $summary, SQLITE3_INTEGER);
    } else if ($title and $link and $lang) {
        $stmt = "INSERT INTO Feeds (Title, Link, Language) VALUES (:Title, :Link, :Language)";
        $stmt = $db->prepare($stmt);
        $stmt->bindValue(":Title", $title, SQLITE3_TEXT);
        $stmt->bindValue(":Link", $link, SQLITE3_TEXT);
        $stmt->bindValue(":Language", $lang, SQLITE3_INTEGER);
    }
    $res = $stmt->execute();

    if ($res) {
        $stmt = "SELECT FeedID FROM Feeds WHERE Title=:Title AND Link=:Link";
        $stmt = $db->prepare($stmt);
        $stmt->bindValue(":Title", $title, SQLITE3_TEXT);
        $stmt->bindValue(":Link", $link, SQLITE3_TEXT);
        $res = $stmt->execute()->fetcharray();
        $feed_id = $res['FeedID'];

        $stmt = "INSERT INTO Display (UserID, FeedID) VALUES (:UserID, :FeedID)";
        $stmt = $db->prepare($stmt);
        $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
        $stmt->bindValue(":FeedID", $feed_id, SQLITE3_INTEGER);
        $stmt->execute();
    }
}

$db->close();
$_GET = $_POST;
include "../settings.php";
?>
