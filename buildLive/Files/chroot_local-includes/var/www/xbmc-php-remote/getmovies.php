<?php

include "topline.php";
include "config.php";

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//prepare the field values being posted to the service
$request = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params" : { "sortorder" : "ascending" }, "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
$array = json_decode(curl_exec($ch),true);

//results movies
$results = $array['result']['movies'];

if(!empty($_GET['playlist'])) {

  //get selected video
  $addplaylist = $_GET['playlist'];

  //clear video playlist
  $data = '{"jsonrpc": "2.0", "method": "VideoPlaylist.Clear", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
  $array = json_decode(curl_exec($ch),true);

  //add video to playlist
  $requestedfile = "$location$addplaylist";

  // to be replaced with video id
  $request = '{"jsonrpc" : "2.0", "method": "VideoPlaylist.Add", "params" : { "file" : "' . $requestedfile . '" }, "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);

  //play item
  $playdata = '{"jsonrpc": "2.0", "method": "VideoPlaylist.Play", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $playdata);
  $array = json_decode(curl_exec($ch),true);
}

echo "<div id=\"utility\"><ul>";

//loop video sources
foreach ($results as $value)
{
  //show video sources
  $sourcename = $value['label'];
  $sourcelocation = urlencode($value['file']);

  //change location to video id
  echo "<li><a href=getmovies.php?playlist=$sourcelocation>$sourcename</a><li>";
}

echo "</ul></div>";

include "downline.php";

?>

