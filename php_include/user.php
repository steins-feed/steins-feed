<?php
if (isset($_GET["user"])) {
    $user = $_GET["user"];
    $stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
    $stmt->bindValue(":Name", $user, SQLITE3_TEXT);
    $res = $stmt->execute()->fetcharray();
    $user_id = $res['UserID'];
} else {
    $stmt = $db->prepare("SELECT * FROM Users ORDER BY UserID");
    $res = $stmt->execute()->fetcharray();
    $user = $res['Name'];
    $user_id = $res['UserID'];
}
?>
