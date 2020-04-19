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

$stmt = $db->prepare("SELECT * FROM Feeds WHERE FeedID=:FeedID");
$stmt->bindValue(':FeedID', $_GET['feed'], SQLITE3_INTEGER);
$feed_it = $stmt->execute()->fetcharray();

$stmt = $db->prepare("SELECT * FROM Display WHERE UserID=:UserID AND FeedID=:FeedID");
$stmt->bindValue(':UserID', $user_id, SQLITE3_INTEGER);
$stmt->bindValue(':FeedID', $_GET['feed'], SQLITE3_INTEGER);
$displayed = $stmt->execute()->fetcharray();

$stmt = $db->prepare("SELECT DISTINCT Tags.* FROM Tags INNER JOIN Tags2Feeds USING (TagID) WHERE UserID=:UserID AND FeedID=:FeedID ORDER BY Name COLLATE NOCASE");
$stmt->bindValue(':UserID', $user_id, SQLITE3_INTEGER);
$stmt->bindValue(':FeedID', $_GET['feed'], SQLITE3_INTEGER);
$res = $stmt->execute();

$tagged = array();
for ($tag_it = $res->fetcharray(); $tag_it; $tag_it = $res->fetcharray()) {
    $tagged[] = $tag_it;
}

$stmt = $db->prepare("SELECT DISTINCT Tags.* FROM Tags WHERE UserID=:UserID AND TagID NOT IN (SELECT DISTINCT TagID FROM Tags INNER JOIN Tags2Feeds USING (TagID) WHERE UserID=:UserID AND FeedID=:FeedID) ORDER BY Name COLLATE NOCASE");
$stmt->bindValue(':UserID', $user_id, SQLITE3_INTEGER);
$stmt->bindValue(':FeedID', $_GET['feed'], SQLITE3_INTEGER);
$res = $stmt->execute();

$untagged = array();
for ($tag_it = $res->fetcharray(); $tag_it; $tag_it = $res->fetcharray()) {
    $untagged[] = $tag_it;
}
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
var feed_id="<?php echo $_GET['feed'];?>";
</script>
<?php
$f_list = array("open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js", "toggle_request.js");
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
<h1><?php echo $feed_it['Title'];?></h1>
</header>
<hr>
<form method="post" action="/steins-feed/php_settings/update_feed.php">
<p>
Title:<br>
<input type="text" name="title" value="<?php echo $feed_it['Title'];?>">
</p>
<p>
Link:<br>
<input type="text" name="link" value="<?php echo $feed_it['Link'];?>">
</p>
<p>
Language:<br>
<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/select_lang.php";
select_lang($feed_it['Language']);
?>
</p>
<p>
Summary:<br>
<?php if ($feed_it['Summary'] == 0):?>
<input type="radio" name="summary" value=0 checked>
<?php else:?>
<input type="radio" name="summary" value=0>
<?php endif;?>
No abstract
<?php if ($feed_it['Summary'] == 1):?>
<input type="radio" name="summary" value=1 checked>
<?php else:?>
<input type="radio" name="summary" value=1>
<?php endif;?>
First paragraph
<?php if ($feed_it['Summary'] == 2):?>
<input type="radio" name="summary" value=2 checked>
<?php else:?>
<input type="radio" name="summary" value=2>
<?php endif;?>
Full abstract
</p>
<p>
Display:<br>
<?php if ($displayed):?>
<input type="radio" name="display" value=1 checked>
<?php else:?>
<input type="radio" name="display" value=1>
<?php endif;?>
Displayed
<?php if (!$displayed):?>
<input type="radio" name="display" value=0 checked>
<?php else:?>
<input type="radio" name="display" value=0>
<?php endif;?>
Hidden
</p>
<input type="hidden" name="user" value=<?php echo $user;?>>
<input type="hidden" name="feed" value=<?php echo $_GET['feed'];?>>
<input type="submit" value="Update feed">
</form>
<hr>
<p>Tags:</p>
<select name="tagged" style="width: 100px;" multiple>
<?php foreach ($tagged as $tag_it):?>
<option value=<?php echo $tag_it['TagID'];?>>
<?php echo $tag_it['Name'], PHP_EOL;?>
</option>
<?php endforeach;?>
</select>
<button onclick="toggle_tags()" type="button">
<i class="material-icons">compare_arrows</i>
</button>
<select name="untagged" style="width: 100px;" multiple>
<?php foreach ($untagged as $tag_it):?>
<option value=<?php echo $tag_it['TagID'];?>>
<?php echo $tag_it['Name'], PHP_EOL;?>
</option>
<?php endforeach;?>
</select>
<hr>
</main>
</body>
</html>
<?php
$db->exec("END");
$db->close();
?>
