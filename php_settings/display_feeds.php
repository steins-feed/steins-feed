<?php $db = new SQLite3("../steins.db");?>
<?php $_GET = $_POST;?>
<?php include "../php_include/user.php";?>
<?php include "../php_include/langs.php";?>
<?php include "../php_include/page.php";?>
<?php include "../php_include/feed.php";?>
<?php include "../php_include/clf.php";?>
<?php
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

include "../index.php";
?>
