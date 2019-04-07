<?php
function foo() {
	if( $_GET["page"] ) {
		$page = $_GET["page"];
	} else {
		$page = 0;
	}
	system('env PYTHONIOENCODING=UTF-8 python3 steins_server.py ' . $page);
}
?>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Stein's Feed</title>
</head>
<body>
<?php foo()?>
</body>
</html>
