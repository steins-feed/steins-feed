<?php
if( $_GET["clf"] ) {
    $clf = $_GET["clf"];
} else {
    $clf_dict = json_decode(file_get_contents("json/steins_magic.json"), true);
    foreach ($clf_dict as $clf_it => $clf_val) {
        $clf = $clf_it;
        break;
    }
}
?>
