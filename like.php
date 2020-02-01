<?php
// ini_set('display_errors', 1);
// ini_set('display_startup_errors', 1);
// error_reporting(E_ALL);

$db = new SQLite3("steins.db");

$user = $_POST["user"];
$item_id = $_POST['id'];
$submit = $_POST['submit'];

if ($submit == "Like") {
    $val = 1;
}
if ($submit == "Dislike") {
    $val = -1;
}

$stmt = sprintf("SELECT %s FROM Like WHERE ItemID=:ItemID", $user);
$stmt = $db->prepare($stmt);
$stmt->bindValue(":ItemID", $item_id, SQLITE3_INTEGER);
$row_val = $stmt->execute()->fetcharray()[0];

$stmt = sprintf("UPDATE Like SET %s=:Like WHERE ItemID=:ItemID", $user);
$stmt = $db->prepare($stmt);
$stmt->bindValue(":ItemID", $item_id, SQLITE3_INTEGER);
if ($row_val == $val) {
    $stmt->bindValue(":Like", 0, SQLITE3_INTEGER);
} else {
    $stmt->bindValue(":Like", $val, SQLITE3_INTEGER);
}
$stmt->execute();

$db->close();
?>
