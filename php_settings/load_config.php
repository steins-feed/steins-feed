<?php $db = new SQLite3("../steins.db");?>
<?php $_GET = $_POST;?>
<?php include "../php_include/user.php";?>
<?php
$feeds = simplexml_load_file($_FILES["feeds"]["tmp_name"]);

foreach ($feeds->feed as $feed_it) {
    $title = $feed_it->title;
    $link = $feed_it->link;
    $lang = $feed_it->lang;
    $summary = $feed_it->summary;

    if ($title and $link and $lang and $summary) {
        $stmt = "INSERT OR IGNORE INTO Feeds (Title, Link, Language, Summary) VALUES (:Title, :Link, :Language, :Summary)";
        $stmt = $db->prepare($stmt);
        $stmt->bindValue(":Title", $title, SQLITE3_TEXT);
        $stmt->bindValue(":Link", $link, SQLITE3_TEXT);
        $stmt->bindValue(":Language", $lang, SQLITE3_TEXT);
        $stmt->bindValue(":Summary", $summary, SQLITE3_INTEGER);
    } else if ($title and $link and $lang) {
        $stmt = "INSERT OR IGNORE INTO Feeds (Title, Link, Language) VALUES (:Title, :Link, :Language)";
        $stmt = $db->prepare($stmt);
        $stmt->bindValue(":Title", $title, SQLITE3_TEXT);
        $stmt->bindValue(":Link", $link, SQLITE3_TEXT);
        $stmt->bindValue(":Language", $lang, SQLITE3_INTEGER);
    }
    $stmt->execute();

    $stmt = "SELECT FeedID FROM Feeds WHERE Title=:Title AND Link=:Link";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":Title", $title, SQLITE3_TEXT);
    $stmt->bindValue(":Link", $link, SQLITE3_TEXT);
    $res = $stmt->execute()->fetcharray();
    $feed_id = $res['FeedID'];

    $stmt = "INSERT OR IGNORE INTO Display (UserID, FeedID) VALUES (:UserID, :FeedID)";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(":FeedID", $feed_id, SQLITE3_INTEGER);
    $stmt->execute();
}

include "../settings.php";
?>
