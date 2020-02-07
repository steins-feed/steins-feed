<?php $db = new SQLite3("../steins.db");?>
<?php $_GET = $_POST;?>
<?php include "../php_include/user.php";?>
<?php
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
<lang><?php if ($row_it['Language']) echo $row_it['Language'];?></lang>
<summary><?php if ($row_it['Summary']) echo $row_it['Summary'];?></summary>
</feed>
<?php endfor;?>
</root>
