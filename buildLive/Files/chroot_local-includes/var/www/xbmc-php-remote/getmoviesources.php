<?php

include "topline.php";
include "config.php";

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//prepare the field values being posted to the service
$request = '{"jsonrpc": "2.0", "method": "Files.GetSources", "params" : { "media" : "video" }, "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
$array = json_decode(curl_exec($ch),true);
$results = $array['result']['shares'];

echo "<div id=\"utility\"><ul>";

//loop video sources
foreach ($results as $value)
{
  //show video sources
  $sourcename = $value['label'];
  $sourcelocation = urlencode($value['file']);
  echo "<li><a href=getvideofiles.php?source=$sourcelocation>$sourcename</a><li>";
}

echo "</ul></div>";

include "downline.php";

?>

