<?php

include "topline.php";
include "config.php";

$tvshowid = $_GET['tvshowid'];
$season = $_GET['season'];

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//prepare the field values being posted to the service
$request = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes", "params": { "tvshowid": ' . $tvshowid . ', "season" : ' . $season . ', "fields": ["episode"], "sort": { "order": "ascending", "method": "episode" } }, "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
$array = json_decode(curl_exec($ch),true);

//results seasons
$results = $array['result']['episodes'];

if(!empty($_GET['playlist'])) {

  //get selected video
  $addplaylist = $_GET['playlist'];

  //clear video playlist
  $data = '{"jsonrpc": "2.0", "method": "VideoPlaylist.Clear", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
  $array = json_decode(curl_exec($ch),true);

  // to be replaced with video id
  $request = '{"jsonrpc" : "2.0", "method": "VideoPlaylist.Add", "params" : { "file" : "' . $addplaylist . '" }, "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);

  //play item
  $playdata = '{"jsonrpc": "2.0", "method": "VideoPlaylist.Play", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $playdata);
  $array = json_decode(curl_exec($ch),true);
}

echo "<div id=\"utility\"><ul>";

//loop seasons
foreach ($results as $value)
{
  //show sources
  $label = $value['label'];
  $file = urlencode($value['file']);

  //change location to video id
  echo "<li><a href=getepisodes.php?tvshowid=$tvshowid&season=$season&playlist=$file>$label</a><li>";
}

echo "</ul></div>";

include "downline.php";

?>

