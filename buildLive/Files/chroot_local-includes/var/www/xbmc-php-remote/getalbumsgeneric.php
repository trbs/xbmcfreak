<?php

include "topline.php";
include "config.php";

//array_sort functie
function array_sort($a, $b) { return strnatcmp($a['label'], $b['label']); }

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//prepare the field values being posted to the service
$data = '{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
$array = json_decode(curl_exec($ch),true);
$results = $array['result'];

echo "<div id=\"utility\"><ul>";
echo "<li><a href=getartists.php>Artists</a><br></li>";
echo "</ul></div>";

$albums = $results['albums'];

//sort songs
usort($albums, 'array_sort');

echo "<div id=\"utility\"><ul>";

//show all music sources, artist is unknown at this stage
foreach ($albums as $value)
{
  $album =  $value['label'];
  $albumid = $value['albumid'];
  $urlalbum = urlencode($album);
  echo "<li><a href=getsongs.php?artist=album=$urlalbum&albumid=$albumid&artist=unknown>$album</a></li>";
}

echo "</ul></div>";

include "downline.php";

?>

