<?php

include "topline.php";
include "config.php";

$tvshowid = $_GET['tvshowid'];

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//prepare the field values being posted to the service
$request = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetSeasons", "params": { "tvshowid": ' . $tvshowid . ', "fields": ["season"]}, "id": 1}';
//echo $request;
curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
$array = json_decode(curl_exec($ch),true);

//results seasons
$results = $array['result']['seasons'];

echo "<div id=\"utility\"><ul>";

//loop seasons
foreach ($results as $value)
{
  //show sources
  $label = $value['label'];
  $season = urlencode($value['season']);

  //change location to video id
  echo "<li><a href=getepisodes.php?tvshowid=$tvshowid&season=$season>$label</a><li>";
}

echo "</ul></div>";

include "downline.php";

?>

