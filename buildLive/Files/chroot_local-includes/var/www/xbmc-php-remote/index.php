<?php include "browserdetect.php"; ?>

<html>
<head>

<?php if ($iphone == '1'): ?>
<meta name="viewport" content="width=320" />
<link rel="stylesheet" href="css/safari-mobile.css" title="default" type="text/css">
<?php elseif ($iphone == '2'): ?>
<meta name="viewport" content="width=980" />
<link rel="stylesheet" href="css/safari-mobile.css" title="default" type="text/css">
<?php else: ?>
<link rel="stylesheet" href="css/desktop.css" title="default" type="text/css">
<?php endif; ?>
<title>XBMC Remote</title>
</head>
<?php if ($iphone == '1'): ?>
<frameset rows="35,*" border="0">
  <frame src="top.php" name="top">
  <frame src="main.php" name="main">
<?php elseif ($iphone == '2'): ?>
<frameset rows="35,*" border="0">
  <frame src="top.php" name="top">
  <frame src="main.php" name="main">
<?php else: ?>
<frameset rows="55,*" border="0">
  <frame src="top.php" name="top" scrolling="no">
  <frame src="main.php" name="main">
<?php endif; ?>
</frameset>
</html>
