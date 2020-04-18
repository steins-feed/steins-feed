<aside id="sidenav" class="sidenav">
<nav class="topnav">
<span class="right">
<a href="/steins-feed/statistics.php?user=<?php echo $user;?>"><i class="material-icons">insert_chart_outlined</i></a>
<a href="/steins-feed/settings.php?user=<?php echo $user;?>"><i class="material-icons">settings</i></a>
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
$feed_dict = array(
    "Full" => "disable_clf()",
    "Magic" => "enable_clf()",
    "Surprise" => "enable_clf()"
);
$clf_dict = json_decode(file_get_contents($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/json/steins_magic.json"), true);
$clf_key = key($clf_dict);
$magic_exists = file_exists($_SERVER['DOCUMENT_ROOT'] . "/steins-feed/$user_id/$clf_key/clfs.pickle");
foreach($feed_dict as $key => $value):
    if ($key == $feed):
        if ($key == "Full" or $magic_exists):
?>
<input name="feed" value="<?php echo $key;?>" type="radio" onclick="<?php echo $value;?>" checked><?php echo $key;?><br>
<?php   else:?>
<input name="feed" value="<?php echo $key;?>" type="radio" onclick="<?php echo $value;?>" checked disabled><?php echo $key;?><br>
<?php   endif;?>
<?php
    else:
        if ($key == "Full" or $magic_exists):
?>
<input name="feed" value="<?php echo $key;?>" type="radio" onclick="<?php echo $value;?>"><?php echo $key;?><br>
<?php   else:?>
<input name="feed" value="<?php echo $key;?>" type="radio" onclick="<?php echo $value;?>" disabled><?php echo $key;?><br>
<?php
        endif;
    endif;
endforeach;
?>
<p>Algorithm:</p>
<?php
foreach ($clf_dict as $clf_it => $clf_val):
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
<input name="timeunit" value="<?php echo $timeunit;?>" type="hidden">
<input name="new_timeunit" value="Day" type="submit">
<input name="new_timeunit" value="Week" type="submit">
<input name="new_timeunit" value="Month" type="submit">
</p>
</form>
</section>
<hr>
<?php if ($feed != 'Full'):?>
<section>
<form action="/steins-feed/analysis.php" method="get">
<p>
<select name="clf">
<?php
    foreach ($clf_dict as $clf_it => $clf_val):
        if ($clf_it == $clf):
?>
<option value="<?php echo $clf_it;?>" selected><?php echo $clf_it;?></option>
<?php   else:?>
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
</section>
<hr>
<?php endif;?>
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
