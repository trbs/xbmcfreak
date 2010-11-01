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

</head>
<body>
<div id="container">
 <center>
 <div id="header">
  <h1>
  <a href="main.php" target="main">XBMC PHP Remote</a>
  </h1>
 </div>
 </center>
</div>
</body>
</html>
