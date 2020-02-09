<?php
$_SERVER['DOCUMENT_ROOT'] = $_SERVER['PWD'] . "/..";
$_POST['user'] = "nobody";
$_FILES["feeds"]["tmp_name"] = $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/feeds.xml";

ob_start();
include $_SERVER['DOCUMENT_ROOT'] . "/steins-feed/php_settings/load_config.php";
ob_end_clean();
?>
