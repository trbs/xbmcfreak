<?php

include "topline.php";
include "config.php";

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//prepare the field values being posted to the service
$request = '{"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows", "params" : { "sortorder" : "ascending" }, "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
$array = json_decode(curl_exec($ch),true);

//results tv shows
$results = $array['result']['tvshows'];

echo "<div id=\"utility\"><ul>";

//loop tvshows
foreach ($results as $value)
{
  //show sources
  $label = $value['label'];
  $tvshowid = urlencode($value['tvshowid']);

  //change location to video id
  echo "<li><a href=getseasons.php?tvshowid=$tvshowid>$label</a><li>";
}

echo "</ul></div>";

include "downline.php";

?>

