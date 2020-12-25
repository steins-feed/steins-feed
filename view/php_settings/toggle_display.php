<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);
$db->exec("BEGIN");

$user = $_POST['user'];
$tagged = json_decode($_POST['displayed'], true);
$untagged = json_decode($_POST['hidden'], true);

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $user, SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

foreach ($tagged as $feed_it) {
    $stmt = "DELETE FROM Display WHERE UserID=:UserID AND FeedID=:FeedID";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(':UserID', $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(':FeedID', $feed_it, SQLITE3_INTEGER);
    $stmt->execute();
}

foreach ($untagged as $feed_it) {
    $stmt = "INSERT OR IGNORE INTO Display (UserID, FeedID) VALUES (:UserID, :FeedID)";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(':UserID', $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(':FeedID', $feed_it, SQLITE3_INTEGER);
    $stmt->execute();
}

$db->exec("END");
$db->close();
?>
