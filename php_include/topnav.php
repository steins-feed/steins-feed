<nav class="topnav">
<span class="left">
<?php
if ($page > 0):
    $link = "/steins-feed/index.php";
    $link .= "?user=" . $user;
    foreach ($langs as $lang_ct => $lang_it) {
        $link .= "&lang_" . $lang_ct . "=" . $lang_it;
    }
    foreach ($tags as $tag_ct => $tag_it) {
        $link .= "&tag_" . $tag_ct . "=" . $tag_it;
    }
    $link .= "&page=" . ($page - 1);
    $link .= "&feed=" . $feed;
    $link .= "&clf=" . $clf;
    $link .= "&timeunit=" . $timeunit;
?>
<a href="<?php echo $link;?>" accesskey="h"><i class="material-icons">fast_rewind</i></a>
<?php else: ?>
<i class="material-icons dead_link">fast_rewind</i>
<?php
endif;
if (!empty($items)):
?>
<i onclick="next_item()" class="material-icons" accesskey="j">expand_more</i>
<i onclick="prev_item()" class="material-icons" accesskey="k">expand_less</i>
<?php else:?>
<i class="material-icons dead_link">expand_more</i>
<i class="material-icons dead_link">expand_less</i>
<?php
endif;
if ($page < count($dates) - 1):
    $link = "/steins-feed/index.php";
    $link .= "?user=" . $user;
    foreach ($langs as $lang_ct => $lang_it) {
        $link .= "&lang_" . $lang_ct . "=" . $lang_it;
    }
    foreach ($tags as $tag_ct => $tag_it) {
        $link .= "&tag_" . $tag_ct . "=" . $tag_it;
    }
    $link .= "&page=" . ($page + 1);
    $link .= "&feed=" . $feed;
    $link .= "&clf=" . $clf;
    $link .= "&timeunit=" . $timeunit;
?>
<a href="<?php echo $link;?>" accesskey="l"><i class="material-icons">fast_forward</i></a>
<?php else: ?>
<i class="material-icons dead_link">fast_forward</i>
<?php
endif;
?>
</span>
<span class="right">
<a href="/steins-feed/statistics.php?user=<?php echo $user;?>" target="_blank"><i class="material-icons">insert_chart_outlined</i></a>
<a href="/steins-feed/settings.php?user=<?php echo $user;?>" target="_blank"><i class="material-icons">settings</i></a>
<i onclick="open_menu()" class="material-icons">
menu
</i>
</span>
</nav>
