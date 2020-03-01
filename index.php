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

// Last updated.
$stmt = $db->prepare("SELECT MIN(Updated) From Feeds");
$res = $stmt->execute()->fetcharray();
$last_updated = $res[0];

// Dates.
$stmt = "SELECT DISTINCT
             datetime(Published, %s)
         FROM
             (Items
             INNER JOIN Feeds USING (FeedID))
             INNER JOIN Display USING (FeedID)
         WHERE
             UserID=:UserID
             AND Published<:Published
         ORDER BY
             Published DESC
         LIMIT
             %d";
if ($timeunit == 'Day') {
    $stmt = sprintf($stmt, "'start of day'", $page + 2);
} else if ($timeunit == 'Week') {
    $stmt = sprintf($stmt, "'weekday 0', '-6 days', 'start of day'", $page + 2);
} else if ($timeunit == 'Month') {
    $stmt = sprintf($stmt, "'start of month'", $page + 2);
}
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
$date_it = end($dates);
if (count($dates) == $page + 2) {
    $date_it = prev($dates);
}
$date_it = new DateTime($date_it);

// Items.
$clf_dict = json_decode(file_get_contents($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/json/steins_magic.json"), true);
$stmt = "
SELECT
    Items.*,
    MIN(Feeds.Title) AS Feed,
    Language,
    IFNULL(Like.Score, 0) AS Like";
if ($feed != 'Full') {
    $stmt .= sprintf(",
    %s.Score", $clf_dict[$clf]['table']);
}
$stmt .= "
FROM";
$temp = "
    Items
    INNER JOIN Feeds USING (FeedID)";
$temp = "(" . $temp . ")";
$temp .= "
    INNER JOIN Display USING (FeedID)";
if (!empty($tags)) {
    $temp = "(" . $temp . ")";
    $temp .= "
    INNER JOIN Tags2Feeds USING (FeedID)";
    $temp = "(" . $temp . ")";
    $temp .= "
    INNER JOIN Tags USING (TagID, UserID)";
}
$temp = "(" . $temp . ")";
$temp .= "
    LEFT JOIN Like USING (UserID, ItemID)";
if ($feed != 'Full') {
    $temp = "(" . $temp . ")";
    $temp .= sprintf("
    LEFT JOIN %s USING (UserID, ItemID)", $clf_dict[$clf]['table']);
}
$stmt .= $temp;
$stmt .= "
WHERE
    UserID=:UserID
    AND (%s)
    AND Published BETWEEN :Start AND :Finish
    AND Published<:Time";
$stmt = sprintf($stmt, $stmt_lang);
if (!empty($tags)) {
    $stmt .= sprintf("
    AND (%s) ", $stmt_tag);
}
$stmt .= "
GROUP BY
    Items.Title,
    Published";
if ($feed == 'Full') {
    $stmt .= "
ORDER BY
    Published DESC";
} else if ($feed == 'Magic') {
    $stmt .= sprintf("
ORDER BY
    %s.Score DESC", $clf_dict[$clf]['table']);
}
$stmt = $db->prepare($stmt);
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
$start_time = $date_it->format("Y-m-d H:i:s");
$stmt->bindValue(":Start", $start_time, SQLITE3_TEXT);
$finish_time = clone $date_it;
$finish_time->add(new DateInterval("P1" . $timeunit[0]));
$finish_time->sub(new DateInterval("PT1S"));
$finish_time = $finish_time->format("Y-m-d H:i:s");
$stmt->bindValue(":Finish", $finish_time, SQLITE3_TEXT);
$stmt->bindValue(":Time", $last_updated, SQLITE3_TEXT);
for ($i = 0; $i < count($langs); $i++) {
    $stmt->bindValue(":Language_" . $i, $langs[$i], SQLITE3_TEXT);
}
for ($i = 0; $i < count($tags); $i++) {
    $stmt->bindValue(":Tag_" . $i, $tags[$i], SQLITE3_TEXT);
}
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
    $db->exec("END");
    $bash_cmd = "python3 " . $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/aux/apply_magic.py " . escapeshellarg($user_id) . " " . escapeshellarg($clf) . " " . escapeshellarg(json_encode($unclassified));
    $res = shell_exec($bash_cmd);
    $classified = json_decode($res, true);
    $db->exec("BEGIN");

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
    $indices = array();
    while (true) {
        $val = rand() / getrandmax() * $probs_total;
        $idx = choice($probs_partial, $val);

        if (in_array($idx, $indices)) {
            continue;
        } else {
            $items_temp[] = $items[$idx];
            $indices[] = $idx;
        }

        if (count($indices) == 10) {
            break;
        }
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
<script>
var user="<?php echo $user;?>";
var clf="<?php echo $clf;?>";
</script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
<?php
$f_list = array("like.js", "dislike.js", "open_menu.js", "close_menu.js", "enable_clf.js", "disable_clf.js");
foreach ($f_list as $f_it):
?>
<script src="/steins-feed/js/<?php echo $f_it;?>" defer></script>
<?php
endforeach;
if ($feed != 'Full'):
    $f_list = array("highlight.js");
    foreach ($f_list as $f_it):
?>
<script src="/steins-feed/js/<?php echo $f_it;?>" defer></script>
<?php endforeach;?>
<script>
<?php foreach ($langs_disp as $lang_it):?>
var <?php echo strtolower($lang_it);?>_words;
$(document).ready(function() {
    $.getJSON("/steins-feed/<?php echo $user_id;?>/<?php echo $clf;?>/<?php echo $lang_it;?>_cookie.json", function(result) {
        <?php echo strtolower($lang_it);?>_words = result;
    });
});
<?php endforeach;?>
</script>
<script src="/steins-feed/snowball/base-stemmer.js" defer></script>
<?php foreach ($langs_disp as $lang_it):?>
<script src="/steins-feed/snowball/<?php echo strtolower($lang_it);?>-stemmer.js" defer></script>
<?php
    endforeach;
endif;
?>
</head>
<body>
<?php
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/topnav.php";

$current_date = new DateTime();
$current_date->setTime(0, 0, 0, 0);

if ($timeunit == 'Day') {
    if ($date_it == $current_date) {
        $topnav_title = "Today";
    } else if ($date_it == $current_date->sub(new DateInterval("P1D"))) {
        $topnav_title = "Yesterday";
    } else {
        $topnav_title = $date_it->format("D, d M Y");
    }
} else if ($timeunit == 'Week') {
    $delta = intval($current_date->format("N")) - 1;
    $date_delta = new DateInterval("P" . strval($delta) . "D");
    $current_date->sub($date_delta);

    if ($date_it == $current_date) {
        $topnav_title = "This Week";
    } else if ($date_it == $current_date->sub(new DateInterval("P1W"))) {
        $topnav_title = "Last Week";
    } else {
        $finish_date = clone $date_it;
        $finish_date->add(new DateInterval("P1W"))->sub(new DateInterval("P1D"));
        $topnav_title = "Week " . $date_it->format("N") . ", " . $date_it->format("Y");
    }
} else if ($timeunit == 'Month') {
    $delta = intval($current_date->format("j")) - 1;
    $date_delta = new DateInterval("P" . strval($delta) . "D");
    $current_date->sub($date_delta);

    if ($date_it == $current_date) {
        $topnav_title = "This Month";
    } else if ($date_it == $current_date->sub(new DateInterval("P1M"))) {
        $topnav_title = "Last Month";
    } else {
        $finish_date = clone $date_it;
        $finish_date->add(new DateInterval("P1M"))->sub(new DateInterval("P1D"));
        $topnav_title = $date_it->format("F Y");
    }
}

topnav($topnav_title);

include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_include/sidenav.php";
?>
<div class="main">
<p>
<?php echo count($items);?> articles.
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
Published: <?php echo $item_it['Published'];?> GMT.
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
<?php if ($feed != 'Full'):?>
<button onclick="highlight(<?php echo $item_it['ItemID'];?>, '<?php echo $item_it['Language'];?>')" type="button">
<i class="material-icons">
<span id="highlight_<?php echo $item_it['ItemID'];?>" class="highlight">lightbulb_outline</span>
</i>
</button>
<?php endif;?>
</p>
</div>
<?php endforeach;?>
<hr>
</div>
</body>
</html>
<?php
$db->exec("END");
$db->close();
?>
