<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);
$db->exec("BEGIN");

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $_POST['user'], SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

$stmt = $db->prepare("SELECT FeedID FROM Feeds");
$res = $stmt->execute();
$feeds = array();
for ($res_it = $res->fetcharray(); $res_it; $res_it = $res->fetcharray()) {
    $feeds[] = $res_it['FeedID'];
}

foreach ($feeds as $feed_it) {
    if ($_POST[$feed_it]) {
        $stmt = "INSERT OR IGNORE INTO Display (UserID, FeedID) VALUES (:UserID, :FeedID)";
    } else {
        $stmt = "DELETE FROM Display WHERE UserID=:UserID AND FeedID=:FeedID";
    }
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(":FeedID", $feed_it, SQLITE3_INTEGER);
    $stmt->execute();
}

$db->exec("END");
$db->close();
$_GET = $_POST;
include "../index.php";
?>
