<?php $db = new SQLite3($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/steins.db");?>
<?php include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/user.php";?>
<?php include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/langs.php";?>
<?php include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/page.php";?>
<?php include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/feed.php";?>
<?php include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/clf.php";?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="/steins-feed/index.css" rel="stylesheet" type="text/css">
<link href="/steins-feed/favicon.ico" rel="shortcut icon" type="image/png">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<title>Stein's Feed</title>
<?php
$f_list = array("open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js");
foreach ($f_list as $f_it):
?>
<script>
<?php
    $s = file_get_contents($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/js/" . $f_it);
    $s = str_replace("USER", $user, $s);
    $s = str_replace("CLF", str_replace(" ", "+", $clf), $s);
    echo $s;
?>
</script>
<?php endforeach;?>
</head>
<body>
<?php
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/topnav.php";
topnav($user);
?>
<?php include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/sidenav.php";?>
<div class="main">
<hr>
<form method="post" action="/steins-feed/php_settings/display_feeds.php">
<?php
$stmt = $db->prepare("SELECT DISTINCT Language FROM Feeds ORDER BY Language");
$res = $stmt->execute();
$langs = array();
for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()){
    $langs[] = $row_it['Language'];
}

foreach ($langs as $lang_it):
?>
<h2><?php echo $lang_it;?> feeds</h2>
<?php
    $stmt = $db->prepare("SELECT FeedID FROM Display WHERE UserID=:UserID");
    $stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
    $res = $stmt->execute();
    $displayed = array();
    for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
        $displayed[] = $row_it['FeedID'];
    }

    $stmt = "SELECT * FROM Feeds WHERE Language=:Language ORDER BY Title COLLATE NOCASE";
    $stmt = $db->prepare($stmt);
    $stmt->bindValue(":Language", $lang_it, SQLITE3_TEXT);
    $res = $stmt->execute();
    $feeds = array();
    for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
        $feeds[] = $row_it;
    }

    foreach ($feeds as $row_it):
        if (in_array($row_it['FeedID'], $displayed)):
?>
<input type="checkbox" name=<?php echo $row_it['FeedID'];?> checked>
<?php   else:?>
<input type="checkbox" name=<?php echo $row_it['FeedID'];?>>
<?php   endif;?>
<a href="<?php echo $row_it['Link'];?>">
<?php echo $row_it['Title'], PHP_EOL;?>
</a>
<br>
<?php endforeach;?>
<?php endforeach;?>
<p>
<input type="hidden" name="user" value=<?php echo $user;?>>
<input type="submit" value="Display feeds">
</p>
</form>
<hr>
<form method="post" action="/steins-feed/add_feed.php">
<p>
Title:<br>
<input type="text" name="title">
</p>
<p>
Link:<br>
<input type="text" name="link">
</p>
<p>
Language:<br>
<?php include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/select_lang.php";?>
</p>
<p>
Summary:<br>
<input type="radio" name="summary" value=0>
No abstract
<input type="radio" name="summary" value=1>
First paragraph
<input type="radio" name="summary" value=2 checked>
Full abstract
</p>
<input type="hidden" name="user" value=<?php echo $user;?>>
<input type="submit" value="Add feed">
</form>
<hr>
<form method="post" action="/steins-feed/delete_feed.php">
<p>
<select name="feed">
<?php
$stmt = $db->prepare("SELECT * FROM Feeds ORDER BY Title COLLATE NOCASE");
$res = $stmt->execute();
$feeds = array();
for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
    $feeds[] = $row_it;
}

foreach ($feeds as $row_it):
?>
<option value="<?php echo $row_it['FeedID'];?>">
<?php echo $row_it['Title'], PHP_EOL;?>
</option>
<?php endforeach;?>
</select>
</p>
<input type="hidden" name="user" value=<?php echo $user;?>>
<input type="submit" value="Delete feed">
</form>
<hr>
<form method="post" action="/steins-feed/php_settings/load_config.php" enctype="multipart/form-data">
<p>
<input type="file" name="feeds" value="feeds">
</p>
<p>
<input type="hidden" name="user" value=<?php echo $user;?>>
<input type="submit" value="Load config">
</form>
<hr>
<form method="post" action="/steins-feed/php_settings/export_config.php">
<p>
<input type="hidden" name="user" value=<?php echo $user;?>>
<input type="submit" value="Export config">
</form>
<hr>
<form method="post" action="/steins-feed/add_user.php">
<p>
Name:<br>
<input type="text" name="name">
</p>
<p>
<input type="submit" value="Add user">
</form>
<hr>
<form method="post" action="/steins-feed/rename_user.php">
<p>
New name:<br>
<input type="text" name="name">
</p>
<p>
<input type="hidden" name="user" value=<?php echo $user;?>>
<input type="submit" value="Rename user">
</form>
<hr>
<form method="post" action="/steins-feed/delete_user.php">
<p>
<input type="hidden" name="user" value=<?php echo $user;?>>
<input type="submit" value="Delete user" style="background-color:red">
</form>
<hr>
</div>
</body>
</html>
