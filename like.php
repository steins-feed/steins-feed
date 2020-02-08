<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);

$user = $_POST['user'];
$item_id = $_POST['id'];
$submit = $_POST['submit'];

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $user, SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

if ($submit == "Like") {
    $val = 1;
} else if ($submit == "Dislike") {
    $val = -1;
}

$stmt = $db->prepare("SELECT Score FROM Like WHERE UserID=:UserID AND ItemID=:ItemID");
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
$stmt->bindValue(":ItemID", $item_id, SQLITE3_INTEGER);
$res = $stmt->execute()->fetcharray();

$score = 0;
if ($res) {
    $score = $res['Score'];
    $stmt = $db->prepare("UPDATE Like SET Score=:Score, Updated=datetime('now') WHERE UserID=:UserID AND ItemID=:ItemID");
} else {
    $stmt = $db->prepare("INSERT INTO Like (UserID, ItemID, Score) VALUES (:UserID, :ItemID, :Score)");
}
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
$stmt->bindValue(":ItemID", $item_id, SQLITE3_INTEGER);
if ($score == $val) {
    $stmt->bindValue(":Score", 0, SQLITE3_INTEGER);
} else {
    $stmt->bindValue(":Score", $val, SQLITE3_INTEGER);
}
$stmt->execute();

$db->close();
?>
