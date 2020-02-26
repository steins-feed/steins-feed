<?php
if (isset($_GET["new_timeunit"])) {
    $timeunit = $_GET["new_timeunit"];
    if ($_GET["new_timeunit"] != $_GET["timeunit"]) {
        $page = 0;
    }
} else if (isset($_GET["timeunit"])) {
    $timeunit = $_GET["timeunit"];
} else {
    $timeunit = "Day";
}
?>
