<div id="sidenav" class="sidenav">
<h1 class="sidenav">
<?php 
if (count($dates) >= 2):
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
else:
    echo "&#160;";
endif;
?>
<span onclick="close_menu()" class="onclick">&#215;&nbsp;</span>
</h1>
<form action="/steins-feed/index.php" method="get">
<p>Language:</p>
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
$clf_dict = json_decode(file_get_contents("json/steins_magic.json"), true);
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
<input type="submit" value="Display">
</p>
</form>
<hr>
<form action="/steins-feed/analysis.php" method="get">
<p>
<select name="clf">
<?php
foreach ($clf_dict as $clf_it => $clf_val):
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
