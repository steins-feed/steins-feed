<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READWRITE);

$stmt = $db->prepare("SELECT UserID FROM Users WHERE Name=:Name");
$stmt->bindValue(":Name", $_POST['user'], SQLITE3_TEXT);
$res = $stmt->execute()->fetcharray();
$user_id = $res['UserID'];

header("Content-Description: File Transfer");
header("Content-Type: application/xml");
header("Content-Disposition: attachment; filename=feeds.xml");
?>
<?xml version="1.0"?>
<root>
<?php
$stmt = "SELECT Feeds.* FROM Feeds INNER JOIN Display USING (FeedID) WHERE UserID=:UserID";
$stmt = $db->prepare($stmt);
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
$res = $stmt->execute();

for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()):
?>
<feed>
<title><?php echo htmlentities($row_it['Title'], $flags=ENT_XML1);?></title>
<link><?php echo htmlentities($row_it['Link']);?></link>
<?php if ($row_it['Language']):?>
<lang><?php echo $row_it['Language'];?></lang>
<?php endif;?>
<?php if ($row_it['Summary']):?>
<summary><?php echo $row_it['Summary'];?></summary>
<?php endif;?>
</feed>
<?php endfor;?>
</root>
<?php $db->close();?>
