<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Stein's Feed</title>
</head>
<body>
<?php system('env PYTHONIOENCODING=UTF-8 python3 steins_server.py ' . $_GET["page"]);?>
</body>
</html>
