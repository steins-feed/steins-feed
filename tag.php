<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READONLY);
$db->exec("BEGIN");

include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/user.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/langs.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/page.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/feed.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/clf.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/timeunit.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/tags.php";

$stmt = $db->prepare("SELECT * FROM Tags WHERE TagID=:TagID");
$stmt->bindValue(':TagID', $_GET['tag'], SQLITE3_INTEGER);
$tag_it = $stmt->execute()->fetcharray();

$stmt = $db->prepare("SELECT DISTINCT Feeds.* FROM Feeds INNER JOIN Tags2Feeds USING (FeedID) WHERE TagID=:TagID ORDER BY Title COLLATE NOCASE");
$stmt->bindValue(':TagID', $_GET['tag'], SQLITE3_INTEGER);
$res = $stmt->execute();

$tagged = array();
for ($feed_it = $res->fetcharray(); $feed_it; $feed_it = $res->fetcharray()) {
    $tagged[] = $feed_it;
}

$stmt = $db->prepare("SELECT DISTINCT Feeds.* FROM Feeds WHERE FeedID NOT IN (SELECT DISTINCT FeedID FROM Feeds INNER JOIN Tags2Feeds USING (FeedID) WHERE TagID=:TagID) ORDER BY Title COLLATE NOCASE");
$stmt->bindValue(':TagID', $_GET['tag'], SQLITE3_INTEGER);
$res = $stmt->execute();

$untagged = array();
for ($feed_it = $res->fetcharray(); $feed_it; $feed_it = $res->fetcharray()) {
    $untagged[] = $feed_it;
}

$stmt = $db->prepare("SELECT DISTINCT Language FROM Feeds ORDER BY Language COLLATE NOCASE");
$res = $stmt->execute();

$langs_tag = array();
for ($lang_it = $res->fetcharray(); $lang_it; $lang_it = $res->fetcharray()) {
    $langs_tag[] = $lang_it[0];
}
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="/steins-feed/index.css" rel="stylesheet" type="text/css">
<link href="/steins-feed/favicon.ico" rel="shortcut icon" type="image/png">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<title>Stein's Feed</title>
<script>
var user="<?php echo $user;?>";
var clf="<?php echo $clf;?>";
var tag_id="<?php echo $_GET['tag'];?>";
</script>
<?php
$f_list = array("open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js", "toggle_feeds.js");
foreach ($f_list as $f_it):
?>
<script src="/steins-feed/js/<?php echo $f_it;?>" defer></script>
<?php endforeach;?>
</head>
<body>
<?php
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/topnav.php";
topnav($tag_it['Name']);
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/sidenav.php";
?>
<div class="main">
<hr>
<?php foreach ($langs_tag as $lang_it):?>
<p><?php echo $lang_it;?> feeds:</p>
<select name="tagged_<?php echo $lang_it;?>" size=10 style="width: 200px;" multiple>
<?php
    foreach ($tagged as $feed_it):
        if ($feed_it['Language'] == $lang_it):
?>
<option value=<?php echo $feed_it['FeedID'];?>>
<?php       echo $feed_it['Title'], PHP_EOL;?>
</option>
<?php
        endif;
    endforeach;
?>
</select>
<button onclick="toggle_feeds('<?php echo $lang_it;?>')" type="button">
<i class="material-icons">compare_arrows</i>
</button>
<select name="untagged_<?php echo $lang_it;?>" size=10 style="width: 200px;" multiple>
<?php
    foreach ($untagged as $feed_it):
        if ($feed_it['Language'] == $lang_it):
?>
<option value=<?php echo $feed_it['FeedID'];?>>
<?php       echo $feed_it['Title'], PHP_EOL;?>
</option>
<?php
        endif;
    endforeach;
?>
</select>
<?php endforeach;?>
</div>
</body>
</html>
<?php
$db->exec("END");
$db->close();
?>