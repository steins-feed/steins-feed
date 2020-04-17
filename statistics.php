<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READONLY);
$db->exec("BEGIN");

include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/clf.php";
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/feed.php";
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/langs.php";
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/page.php";
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/tags.php";
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/timeunit.php";
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/user.php";
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="/steins-feed/css/index.css" rel="stylesheet" type="text/css">
<link href="/steins-feed/css/topnav.css" rel="stylesheet" type="text/css">
<link href="/steins-feed/css/sidenav.css" rel="stylesheet" type="text/css">
<link href="/steins-feed/favicon.ico" rel="shortcut icon" type="image/png">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<title>Stein's Feed</title>
<script>
var user="<?php echo $user;?>";
var clf="<?php echo $clf;?>";
</script>
<?php
$f_list = array("open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js");
foreach ($f_list as $f_it):
?>
<script src="/steins-feed/js/<?php echo $f_it;?>" defer></script>
<?php endforeach;?>
</head>
<body>
<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/topnav.php";
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/sidenav.php";
?>
<main>
<header>
<h1><?php echo $user;?></h1>
</header>
<hr>
<?php foreach ($langs_disp as $lang_it):?>
<h2><?php echo $lang_it;?></h2>
<?php
    $stmt = "SELECT Items.*, Feeds.Title AS Feed FROM (Items INNER JOIN Feeds USING (FeedID)) INNER JOIN Like USING (ItemID) WHERE UserID=:UserID AND Score=1 AND Language=:Language ORDER BY Published DESC";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(":Language", $lang_it, SQLITE3_TEXT);
    $res = $stmt->execute();

    $likes = array();
    for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
        $likes[] = $row_it;
    }
?>
<p><?php echo count($likes);?> likes:</p>
<ul>
<?php foreach ($likes as $row_it):?>
<li>
<?php echo $row_it['Feed'];?>:
<a href="<?php echo $row_it['Link'];?>">
<?php echo $row_it['Title'];?>
</a>
<?php $timestamp = new DateTime($row_it['Published']);?>
(<?php echo $timestamp->format("D, d M Y");?>).
</li>
<?php endforeach;?>
</ul>
<?php
    $stmt = "SELECT Items.*, Feeds.Title AS Feed FROM (Items INNER JOIN Feeds USING (FeedID)) INNER JOIN Like USING (ItemID) WHERE UserID=:UserID AND Score=-1 AND Language=:Language ORDER BY Published DESC";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $stmt->bindValue(":Language", $lang_it, SQLITE3_TEXT);
    $res = $stmt->execute();

    $likes = array();
    for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
        $likes[] = $row_it;
    }
?>
<p><?php echo count($likes);?> dislikes:</p>
<ul>
<?php foreach ($likes as $row_it):?>
<li>
<?php echo $row_it['Feed'];?>:
<a href="<?php echo $row_it['Link'];?>">
<?php echo $row_it['Title'];?>
</a>
<?php $timestamp = new DateTime($row_it['Published']);?>
(<?php echo $timestamp->format("D, d M Y");?>).
</li>
<?php endforeach;?>
</ul>
<hr>
<?php endforeach;?>
</main>
</body>
</html>
<?php
$db->exec("END");
$db->close();
?>
