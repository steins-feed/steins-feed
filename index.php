<?php
// ini_set('display_errors', 1);
// ini_set('display_startup_errors', 1);
// error_reporting(E_ALL);

$db = new SQLite3("steins.db");

if( $_GET["user"] ) {
    $user = $_GET["user"];
    $stmt = $db->prepare("SELECT * FROM Users WHERE Name=:Name");
    $stmt->bindValue(":Name", $user, SQLITE3_TEXT);
    $res = $stmt->execute()->fetcharray();
    $user_id = $res['UserID'];
} else {
    $stmt = $db->prepare("SELECT * FROM Users ORDER BY UserID");
    $res = $stmt->execute()->fetcharray();
    $user = $res['Name'];
    $user_id = $res['UserID'];
}

$stmt = $db->prepare("SELECT DISTINCT Language FROM Feeds INNER JOIN Display USING (FeedID) WHERE UserID=:UserID");
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
$res = $stmt->execute();
$langs_nav = array();
for ($res_it = $res->fetcharray(); $res_it; $res_it = $res->fetcharray()) {
    $langs_nav[] = $res_it['Language'];
}

$langs = array();
for ($i = 0; $i < count($langs_nav); $i++) {
    if ($_GET["lang_" . $i]) {
        $langs[] = $_GET["lang_" . $i];
    }
}
if (count($langs) == 0) {
    $langs = $langs_nav;
}

$stmt_lang = "Language=:Language_0";
for ($i = 1; $i < count($langs); $i++) {
    $stmt_lang .= " OR Language=:Language_" . $i;
}

if( $_GET["page"] ) {
    $page = $_GET["page"];
} else {
    $page = "0";
}

if( $_GET["feed"] ) {
    $feed = $_GET["feed"];
} else {
    $feed = "Full";
}

if( $_GET["clf"] ) {
    $clf = $_GET["clf"];
} else {
    $clf = "Naive Bayes";
}

$stmt = $db->prepare("SELECT MIN(Updated) From Feeds");
$res = $stmt->execute()->fetcharray();
$last_updated = $res[0];

// Language.
$stmt = sprintf("SELECT DISTINCT SUBSTR(Published, 1, 10) FROM (Items INNER JOIN Feeds USING (FeedID)) INNER JOIN Display USING (FeedID) WHERE UserID=:UserID AND (%s) AND Published<:Published ORDER BY Published DESC", $stmt_lang);
$stmt = $db->prepare($stmt);
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
for ($i = 0; $i < count($langs); $i++) {
    $stmt->bindValue(":Language_" . $i, $langs[$i], SQLITE3_TEXT);
}
$stmt->bindValue(":Published", $last_updated, SQLITE3_TEXT);

$res = $stmt->execute();
$dates = array();
for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
    $dates[] = $row_it[0];
}
if ($page >= count($dates)) return;

$date_it = new DateTime($dates[$page]);
$stmt = sprintf("SELECT Items.*, Feeds.Title AS Feed, Feeds.Language, IFNULL(Like.Score, 0) AS Like FROM ((Items INNER JOIN Feeds USING (FeedID)) INNER JOIN Display USING (FeedID)) LEFT JOIN Like USING (UserID, ItemID) WHERE UserID=:UserID AND (%s) AND SUBSTR(Published, 1, 10)=:Date AND Published<:Time ORDER BY Published DESC", $stmt_lang);
$stmt = $db->prepare($stmt);
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
for ($i = 0; $i < count($langs); $i++) {
    $stmt->bindValue(":Language_" . $i, $langs[$i], SQLITE3_TEXT);
}
$stmt->bindValue(":Date", $date_it->format("Y-m-d"), SQLITE3_TEXT);
$stmt->bindValue(":Time", $last_updated, SQLITE3_TEXT);

$res = $stmt->execute();
$items = array();
for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
    $items[] = $row_it;
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
<?php
$f_list = array("like.js", "dislike.js", "highlight.js", "open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js");
foreach ($f_list as $f_it):
?>
<script>
<?php
    $s = file_get_contents("js/" . $f_it);
    $s = str_replace("USER", $user, $s);
    $s = str_replace("CLF", str_replace(" ", "+", $clf), $s);
    echo $s;
?>
</script>
<?php endforeach;?>
</head>
<body>
<div class="topnav">
<h1>
<?php echo $date_it->format("D, d M Y"), PHP_EOL;?>
<span class="scroll"></span>
<span onclick="open_menu()" class="onclick">&#9776;&nbsp;</span>
</h1>
</div>
<div id="sidenav" class="sidenav">
<h1 class="sidenav">
<?php 
if (count($dates) == 1):
    echo "&#160;";
else:
    if ($page < count($dates) - 1):
?>
<form action="/steins-feed/index.php" method="get">
<input name="user" value="<?php echo $user;?>" type="hidden">
<?php foreach ($langs as $lang_ct => $lang_it):?>
<input name="lang_<?php echo $lang_ct;?>" value="<?php echo $lang_it;?>" type="hidden">
<?php endforeach;?>
<input name="page" value="<?php echo $page + 1;?>" type="hidden">
<input name="feed" value="<?php echo $feed;?>" type="hidden">
<input name="clf" value="<?php echo $clf;?>" type="hidden">
<button type="submit"><i class="material-icons">fast_rewind</i></button>
</form>
<?php
    endif;
    if ($page > 0):
?>
<form action="/steins-feed/index.php" method="get">
<input name="user" value="<?php echo $user;?>" type="hidden">
<?php foreach ($langs as $lang_ct => $lang_it):?>
<input name="lang_<?php echo $lang_ct;?>" value="<?php echo $lang_it;?>" type="hidden">
<?php endforeach;?>
<input name="page" value="<?php echo $page - 1;?>" type="hidden">
<input name="feed" value="<?php echo $feed;?>" type="hidden">
<input name="clf" value="<?php echo $clf;?>" type="hidden">
<button type="submit"><i class="material-icons">fast_forward</i></button>
</form>
<?php
    endif;
endif;
?>
<span onclick="close_menu()" class="onclick">&#215;&nbsp;</span>
</h1>
<form action="/steins-feed/index.php" method="get">
<p>Language:</p>
<?php
foreach ($langs_nav as $lang_ct => $lang_it):
    if (in_array($lang_it, $langs)):
?>
<input name="lang_<?php echo $lang_ct;?>" value="<?php echo $lang_it;?>" type="checkbox" checked><?php echo $lang_it;?><br>
<?php else:?>
<input name="lang_<?php echo $lang_ct;?>" value="<?php echo $lang_it;?>" type="checkbox"><?php echo $lang_it;?><br>
<?php
    endif;
endforeach;
?>
<p>Feed:</p>
<?php
$feed_dict = array(
    "Full" => "disable_clf()",
    "Magic" => "enable_clf()",
    "Surprise" => "enable_clf()"
);
foreach($feed_dict as $key => $value):
    if ($key == $feed):
?>
<input name="feed" value="<?php echo $key;?>" type="radio" onclick="<?php echo $value;?>" checked><?php echo $key;?><br>
<?php else:?>
<input name="feed" value="<?php echo $key;?>" type="radio" onclick="<?php echo $value;?>"><?php echo $key;?><br>
<?php
    endif;
endforeach;
?>
<p>Algorithm:</p>
<?php
foreach (array("Logistic Regression", "Naive Bayes") as $clf_it):
    if ($feed == "Full"):
        if ($clf_it == $clf):
?>
<input name="clf" value="<?php echo $clf_it;?>" type="radio" class="clf" checked disabled><?php echo $clf_it;?><br>
<?php   else:?>
<input name="clf" value="<?php echo $clf_it;?>" type="radio" class="clf" disabled><?php echo $clf_it;?><br>
<?php
        endif;
    else:
        if ($clf_it == $clf):
?>
<input name="clf" value="<?php echo $clf_it;?>" type="radio" class="clf" checked><?php echo $clf_it;?><br>
<?php   else:?>
<input name="clf" value="<?php echo $clf_it;?>" type="radio" class="clf"><?php echo $clf_it;?><br>
<?php
        endif;
    endif;
endforeach;
?>
<p>
<input name="user" value="<?php echo $user;?>" type="hidden">
<input name="page" value="<?php echo $page;?>" type="hidden">
<input type="submit" value="Display">
</p>
</form>
<hr>
<form action="/steins-feed/analysis.php" method="get">
<p>
<select name="clf">
<?php
foreach (array("Logistic Regression", "Naive Bayes") as $clf_it):
    if ($clf_it == $clf):
?>
<option value="<?php echo $clf_it;?>" selected><?php echo $clf_it;?></option>
<?php else:?>
<option value="<?php echo $clf_it;?>"><?php echo $clf_it;?></option>
<?php
    endif;
endforeach;
?>
</select>
<input name="user" value="<?php echo $user;?>" type="hidden">
<input type="submit" value="Report">
</p>
</form>
<hr>
<p><a href="/steins-feed/statistics.php?user=<?php echo $user;?>">Statistics</a></p>
<p><a href="/steins-feed/settings.php?user=<?php echo $user;?>">Settings</a></p>
<hr>
<p><a href="https://github.com/hy144328/steins-feed">GitHub</a></p>
<p><a href="https://github.com/hy144328/steins-feed/blob/master/HOWTO.md">Instructions</a></p>
</div>
<div class="main">
<p>
<?php echo count($items);?> articles.
<?php echo count($dates);?> pages.
Last updated: <?php echo $last_updated, " GMT";?>.
</p>
<?php foreach ($items as $item_it):?>
<hr>
<div>
<h2>
<a href="<?php echo $item_it['Link']?>" rel="noopener noreferrer" target="_blank">
<span id="title_<?php echo $item_it['ItemID'];?>">
<span><?php echo $item_it['Title'];?></span>
</span>
</a>
</h2>
<p>
Source: <?php echo $item_it['Feed'];?>.
Published: <?php echo $item_it['Published'];?>.
</p>
<div id="summary_<?php echo $item_it['ItemID'];?>">
<div>
<?php echo html_entity_decode($item_it['Summary']), PHP_EOL;?>
</div>
</div>
<p>
<button onclick="like(<?php echo $item_it['ItemID'];?>)" type="button">
<i class="material-icons">
<?php if ($item_it['Like'] == 1):?>
<span id="like_<?php echo $item_it['ItemID'];?>" class="liked">thumb_up</span>
<?php else:?>
<span id="like_<?php echo $item_it['ItemID'];?>" class="like">thumb_up</span>
<?php endif;?>
</i>
</button>
<button onclick="dislike(<?php echo $item_it['ItemID'];?>)" type="button">
<i class="material-icons">
<?php if ($item_it['Like'] == -1):?>
<span id="dislike_<?php echo $item_it['ItemID'];?>" class="disliked">thumb_down</span>
<?php else:?>
<span id="dislike_<?php echo $item_it['ItemID'];?>" class="dislike">thumb_down</span>
<?php endif;?>
</i>
</button>
<button onclick="highlight(<?php echo $item_it['ItemID'];?>)" type="button">
<i class="material-icons">lightbulb_outline</i>
</button>
</p>
</div>
<?php endforeach;?>
</div>
</body>
</html>
