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

<?php
//include port and hostname from config file
include "config.php";

//json rpc call
$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//check if jsonrpc service is running
$data = '{"jsonrpc": "2.0", "method": "JSONRPC.Ping", "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
$array = json_decode(curl_exec($ch),true);

//show options or warning message
if ($array[result] == 'pong') {
?>

<body>
<div id="container">
 <div id="header">
  <div id="utility">
   <ul>
   <li><a href="getalbumsgeneric.php" target="main">Music Albums</a></li>
   <li><a href="getartists.php" target="main">Music Artists</a></li>
   <li><a href="getmusicsources.php" target="main">Music Sources</a></li>
   <li><a href="getmovies.php" target="main">Movies</a></li>
   <li><a href="gettvshows.php" target="main">TV Shows</a></li>
   <li><a href="getmoviesources.php" target="main">Video Sources</a></li>
   <li><a href="remote.php" target="main">Remote Control</a></li>
   <li><a href="getplaylist.php" target="main">Show Playlist</a></li>
   </ul>
  </div>
 </div>
</div>
</body>

<?php } else {

echo "Could not connect to the jsonrpc XBMC service.";
echo "<br><br>";
echo "- Check if the option \"Allow control of XBMC via http\" is enabled in the Network Settings.";
echo "<br>";
echo "- Check if the port number in config.php matches the port number from the Network Settings.";

}

?>

</html>

