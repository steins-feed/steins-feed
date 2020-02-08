<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $_POST["user"], SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

$stmt = $db->prepare("SELECT * FROM Users ORDER BY UserID");
$res = $stmt->execute()->fetcharray();
$default_user_id = $res['UserID'];

if ($user_id != $default_user_id) {
    $stmt = $db->prepare("UPDATE Users SET Name=:Name WHERE UserID=:UserID");
    $stmt->bindValue(":Name", $_POST['name'], SQLITE3_TEXT);
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $res = $stmt->execute();

    $_POST['user'] = $_POST['name'];
}

$db->close();
$_GET = $_POST;
include "../settings.php";
?>
