<aside id="sidenav" class="sidenav">
<nav class="topnav">
<span class="right">
<a href="/steins-feed/statistics.php?user=<?php echo $user;?>" target="_blank"><i class="material-icons">insert_chart_outlined</i></a>
<a href="/steins-feed/settings.php?user=<?php echo $user;?>" target="_blank"><i class="material-icons">settings</i></a>
<i onclick="close_menu()" class="material-icons">
close
</i>
</span>
</nav>
<section>
<form action="/steins-feed/index.php" method="get">
<?php if (count($tags_disp)):?>
<p>Tags:</p>
<?php
    foreach ($tags_disp as $tag_ct => $tag_it):
        if (in_array($tag_it, $tags)):
?>
<input name="tag_<?php echo $tag_ct;?>" value="<?php echo $tag_it;?>" type="checkbox" checked><?php echo $tag_it;?><br>
<?php   else:?>
<input name="tag_<?php echo $tag_ct;?>" value="<?php echo $tag_it;?>" type="checkbox"><?php echo $tag_it;?><br>
<?php
        endif;
    endforeach;
endif;
?>
<p>Languages:</p>
<?php
foreach ($langs_disp as $lang_ct => $lang_it):
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
$feed_dict = array("Full", "Magic", "Surprise");
$clf_dict = json_decode(file_get_contents($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/json/steins_magic.json"), true);
$clf_key = key($clf_dict);
$magic_exists = file_exists($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/$user_id/$clf_key/clfs.pickle");
foreach($feed_dict as $key) {
    $feed_input = '<input name="feed" value="' . $key . '" type="radio"';
    if ($key == $feed) {
        $feed_input .= ' checked';
    }
    if (!$magic_exists) {
        $feed_input .= ' disabled';
    }
    $feed_input .= '>' . $key . '<br>';
    echo $feed_input . PHP_EOL;
}
?>
<p>
<input name="user" value="<?php echo $user;?>" type="hidden">
<input name="page" value="<?php echo $page;?>" type="hidden">
<input name="timeunit" value="<?php echo $timeunit;?>" type="hidden">
<input name="new_timeunit" value="Day" type="submit">
<input name="new_timeunit" value="Week" type="submit">
<input name="new_timeunit" value="Month" type="submit">
</p>
</form>
</section>
<hr>
<form action="/steins-feed/tag.php" method="get">
<p>
<select name="tag">
<?php foreach ($tags_disp as $tag_ct => $tag_it):?>
<option value="<?php echo $tags_disp_id[$tag_ct];?>"><?php echo $tags_disp[$tag_ct];?></option>
<?php endforeach;?>
</select>
<input name="user" value="<?php echo $user;?>" type="hidden">
<input type="submit" value="Edit">
</p>
</form>
</aside>
