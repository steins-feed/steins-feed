<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $_POST["user"], SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

$stmt = $db->prepare("SELECT * FROM Users ORDER BY UserID");
$res = $stmt->execute()->fetcharray();
$default_user = $res['Name'];
$default_user_id = $res['UserID'];

if ($user_id != $default_user_id) {
    $stmt = $db->prepare("DELETE FROM Users WHERE UserID=:UserID");
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $stmt->execute();

    $_POST['user'] = $default_user;
}

$db->close();
$_GET = $_POST;
include "../settings.php";
?>
