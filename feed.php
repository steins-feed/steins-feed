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

$stmt = $db->prepare("SELECT * FROM Feeds WHERE FeedID=:FeedID");
$stmt->bindValue(':FeedID', $_GET['feed'], SQLITE3_INTEGER);
$res = $stmt->execute()->fetcharray();

$stmt = $db->prepare("SELECT * FROM Display WHERE UserID=:UserID AND FeedID=:FeedID");
$stmt->bindValue(':UserID', $user_id, SQLITE3_INTEGER);
$stmt->bindValue(':FeedID', $_GET['feed'], SQLITE3_INTEGER);
$displayed = $stmt->execute()->fetcharray();
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
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/topnav.php";
topnav($user);
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/sidenav.php";
?>
<div class="main">
<hr>
<form method="post" action="/steins-feed/php_settings/update_feed.php">
<p>
Title:<br>
<input type="text" name="title" value="<?php echo $res['Title'];?>">
</p>
<p>
Link:<br>
<input type="text" name="link" value="<?php echo $res['Link'];?>">
</p>
<p>
Language:<br>
<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/select_lang.php";
select_lang($res['Language']);
?>
</p>
<p>
Summary:<br>
<?php if ($res['Summary'] == 0):?>
<input type="radio" name="summary" value=0 checked>
<?php else:?>
<input type="radio" name="summary" value=0>
<?php endif;?>
No abstract
<?php if ($res['Summary'] == 1):?>
<input type="radio" name="summary" value=1 checked>
<?php else:?>
<input type="radio" name="summary" value=1>
<?php endif;?>
First paragraph
<?php if ($res['Summary'] == 2):?>
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
</div>
</body>
</html>
<?php
$db->exec("END");
$db->close();
?>
