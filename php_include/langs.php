<?php
$stmt = $db->prepare("SELECT DISTINCT Language FROM Feeds INNER JOIN Display USING (FeedID) WHERE UserID=:UserID");
$stmt->bindValue(":UserID", $user_id, SQLITE3_INTEGER);
$res = $stmt->execute();
$langs_disp = array();
for ($res_it = $res->fetcharray(); $res_it; $res_it = $res->fetcharray()) {
    $langs_disp[] = $res_it['Language'];
}

$langs = array();
for ($i = 0; $i < count($langs_disp); $i++) {
    if ($_GET["lang_" . $i]) {
        $langs[] = $_GET["lang_" . $i];
    }
}
if (count($langs) == 0) {
    $langs = $langs_disp;
}

$stmt_lang = "Language=:Language_0";
for ($i = 1; $i < count($langs); $i++) {
    $stmt_lang .= " OR Language=:Language_" . $i;
}
?>
