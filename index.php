<?php
include_once $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/steins_db.php";
$db = steins_db(SQLITE3_OPEN_READONLY);

include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/user.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/langs.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/page.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/feed.php";
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/clf.php";

// Last updated.
$stmt = $db->prepare("SELECT MIN(Updated) From Feeds");
$res = $stmt->execute()->fetcharray();
$last_updated = $res[0];

// Dates.
$stmt = sprintf("SELECT DISTINCT
                     SUBSTR(Published, 1, 10)
                 FROM
                     (Items
                     INNER JOIN Feeds USING (FeedID))
                     INNER JOIN Display USING (FeedID)
                 WHERE
                     UserID=:UserID
                     AND (%s)
                     AND Published<:Published
                 ORDER BY
                     Published DESC",
                $stmt_lang);
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

// Items.
$clf_dict = json_decode(file_get_contents($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/json/steins_magic.json"), true);
if ($feed == 'Full') {
    $stmt = sprintf("SELECT
                         Items.*,
                         MIN(Feeds.Title) AS Feed,
                         IFNULL(Like.Score, 0) AS Like
                     FROM
                         ((Items
                         INNER JOIN Feeds USING (FeedID))
                         INNER JOIN Display USING (FeedID))
                         LEFT JOIN Like USING (UserID, ItemID)
                     WHERE
                         UserID=:UserID
                         AND (%s)
                         AND Published BETWEEN :Start AND :Finish
                         AND Published<:Time
                     GROUP BY
                         Items.Title,
                         Published
                     ORDER BY
                         Published DESC",
                    $stmt_lang);
} else if ($feed == 'Magic') {
    $stmt = sprintf("SELECT
                         Items.*,
                         MIN(Feeds.Title) AS Feed,
                         IFNULL(Like.Score, 0) AS Like,
                         %s.Score
                     FROM
                         (((Items
                         INNER JOIN Feeds USING (FeedID))
                         INNER JOIN Display USING (FeedID))
                         LEFT JOIN Like USING (UserID, ItemID))
                         LEFT JOIN %s USING (UserID, ItemID)
                     WHERE
                         UserID=:UserID
                         AND (%s)
                         AND Published BETWEEN :Start AND :Finish
                         AND Published<:Time
                     GROUP BY
                         Items.Title,
                         Published
                     ORDER BY
                         %s.Score DESC",
                    $clf_dict[$clf]['table'],
                    $clf_dict[$clf]['table'],
                    $stmt_lang,
                    $clf_dict[$clf]['table']);
} else if ($feed == 'Surprise') {
    $stmt = sprintf("SELECT
                         Items.*,
                         MIN(Feeds.Title) AS Feed,
                         IFNULL(Like.Score, 0) AS Like,
                         %s.Score
                     FROM
                         (((Items
                         INNER JOIN Feeds USING (FeedID))
                         INNER JOIN Display USING (FeedID))
                         LEFT JOIN Like USING (UserID, ItemID))
                         LEFT JOIN %s USING (UserID, ItemID)
                     WHERE
                         UserID=:UserID
                         AND (%s)
                         AND Published BETWEEN :Start AND :Finish
                         AND Published<:Time
                     GROUP BY
                         Items.Title,
                         Published",
                    $clf_dict[$clf]['table'],
                    $clf_dict[$clf]['table'],
                    $stmt_lang);
}
$stmt = $db->prepare($stmt);
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
for ($i = 0; $i < count($langs); $i++) {
    $stmt->bindValue(":Language_" . $i, $langs[$i], SQLITE3_TEXT);
}
$stmt->bindValue(":Start", $date_it->format("Y-m-d") . " 00:00:00", SQLITE3_TEXT);
$stmt->bindValue(":Finish", $date_it->format("Y-m-d") . " 23:59:59", SQLITE3_TEXT);
$stmt->bindValue(":Time", $last_updated, SQLITE3_TEXT);
$res = $stmt->execute();

$items = array();
$unclassified = array();
for ($row_it = $res->fetcharray(); $row_it; $row_it = $res->fetcharray()) {
    $items[] = $row_it;
    if ($feed != 'Full' and is_null($row_it['Score'])) {
        $unclassified[] = $row_it['ItemID'];
    }
}

// Classifiers.
if (!empty($unclassified)) {
    $bash_cmd = "python3 " . $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/aux/apply_magic.py " . escapeshellarg($user_id) . " " . escapeshellarg($clf) . " " . escapeshellarg(json_encode($unclassified));
    $res = shell_exec($bash_cmd);
    $classified = json_decode($res, true);

    for ($i = 0; $i < count($unclassified); $i++) {
        $j = array_search($unclassified[$i], array_column($items, 'ItemID'));
        $items[$j]['Score'] = $classified[$i];
    }

    if ($feed == 'Magic') {
        array_multisort(array_column($items, 'Score'), SORT_DESC, $items);
    }
}

// Surprise.
function choice($probs_partial, $val) {
    $low = 0;
    $high = count($probs_partial) - 1;

    while (true) {
        if ($high == $low + 1) {
            break;
        }

        $temp = intdiv($low + $high, 2);
        if ($probs_partial[$temp] <= $val) {
            $low = $temp;
        } else {
            $high = $temp;
        }
    }

    return $low;
}

if ($feed == 'Surprise') {
    $probs_partial = array();
    $probs_partial[] = 0.;
    for ($item_ct = 0; $item_ct < count($items); $item_ct++) {
        $item_it = $items[$item_ct];
        $log_score = log($item_it['Score'] / (1. - $item_it['Score']));
        $probs_partial[] = $probs_partial[$item_ct] + exp(-$log_score * $log_score);
    }
    $probs_total = $probs_partial[count($items)];

    $items_temp = array();
    for ($i = 0; $i < 10; $i++) {
        $val = rand() / getrandmax() * $probs_total;
        $idx = choice($probs_partial, $val);
        $items_temp[] = $items[$idx];
    }
    $items = $items_temp;
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
<script type="text/javascript">
var user="<?php echo $user;?>";
var clf="<?php echo $clf;?>";
</script>
<?php
$f_list = array("like.js", "dislike.js", "highlight.js", "open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js");
foreach ($f_list as $f_it):
?>
<script type="text/javascript" src="/steins-feed/js/<?php echo $f_it;?>"></script>
<?php endforeach;?>
</head>
<body>
<?php
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/topnav.php";
topnav($date_it->format("D, d M Y"));
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/sidenav.php";
?>
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
<a href="<?php echo htmlentities($item_it['Link'])?>" rel="noopener noreferrer" target="_blank">
<span id="title_<?php echo $item_it['ItemID'];?>">
<span><?php echo $item_it['Title'];?></span>
</span>
</a>
</h2>
<p>
Source: <?php echo $item_it['Feed'];?>.
Published: <?php echo $item_it['Published'];?>.
<?php
if ($feed != 'Full'):
?>
Score: <?php printf("%.2f", 2. * $item_it['Score'] - 1.);?>.
<?php endif;?>
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
<hr>
</div>
</body>
</html>
<?php $db->close();?>
