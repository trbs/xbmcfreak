<?php

include "topline.php";
include "config.php";

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//clear playlist
if(!empty($_GET['argument1']))
{
  //clear audio playlist
  $data = '{"jsonrpc": "2.0", "method": "AudioPlaylist.Clear", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
  $array = json_decode(curl_exec($ch),true);

  //clear video playlist
  $data = '{"jsonrpc": "2.0", "method": "VideoPlaylist.Clear", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
  $array = json_decode(curl_exec($ch),true);
}

//show Audio header
echo "<div id=\"content\"><p>";
echo "AudioPlaylist.GetItems:<br><br>";
echo "</p></div>";

//Get audio playlist
echo "<div id=\"utility\"><ul>";
$audioplaylistdata = '{"jsonrpc": "2.0", "method": "AudioPlaylist.GetItems", "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $audioplaylistdata);
$audioplaylistarray = json_decode(curl_exec($ch),true);
$audioplaylistresults = $audioplaylistarray['result'];
if (array_key_exists('items', $audioplaylistresults))
{
  $results = $audioplaylistresults['items'];
  foreach ($results as $value)
  {
    $inhoud = $value['file'];
    echo "<li><a href=getplaylist.php?argument2=dosomething>$inhoud</a></li><br>\n";
  }
}
echo "</ul></div>";

//break
echo "<br>";

//show video header
echo "<div id=\"content\"><p>";
echo "VideoPlaylist.GetItems:<br><br>";
echo "</p></div>";

//Get video playlist
echo "<div id=\"utility\"><ul>";
$videoplaylistdata = '{"jsonrpc": "2.0", "method": "VideoPlaylist.GetItems", "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $videoplaylistdata);
$videoplaylistarray = json_decode(curl_exec($ch),true);
$videoplaylistresults = $videoplaylistarray['result'];

if (array_key_exists('items', $videoplaylistresults))
{
  $results = $videoplaylistresults['items'];
  foreach ($results as $value)
  {
    $inhoud = $value['file'];
    echo "<li><a href=getplaylist.php?argument2=dosomething>$inhoud</a></li><br>\n";
  }
}
echo "</ul></div>";

//break
echo "<br>";

//clear audio playlist
echo "<div id=\"utility\"><ul>";
echo "<li><a href=getplaylist.php?argument1=clearplaylist>Clear Playlist</a></li>\n";
echo "</ul></div>";

include "downline.php";

?>

