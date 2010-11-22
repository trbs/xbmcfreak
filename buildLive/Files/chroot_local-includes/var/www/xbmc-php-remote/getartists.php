<?php

include "config.php";
include "topline.php";

//display errors and warnings
ini_set('display_errors', 1);
error_reporting(-1);

//init json rpc
$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//prepare the field values being posted to the service
$data = '{"jsonrpc": "2.0", "method": "AudioLibrary.GetArtists", "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
$array = json_decode(curl_exec($ch),true);
$results = $array['result'];

//array_sort function
function array_sort($a, $b) { return strnatcmp($a['label'], $b['label']); }

//show artists button
echo "<div id=\"utility\"><ul>";
echo "<li><a href=getartists.php>Artists</a></li>";
echo "</ul></div>";

//get artists from results
$artists = $results['artists'];

//sort artists on name
usort($artists, 'array_sort');

//show all artists
echo "<div id=\"utility\"><ul>";
foreach ($artists as $value)
{
  $artist =  $value['label'];
  $artistid = $value['artistid'];
  $urlartist = urlencode($artist);
  echo "<li><a href=getalbums.php?artist=$urlartist&artistid=$artistid>$artist</a></li>";
}
echo "</ul></div>";

include "downline.php";

?>

