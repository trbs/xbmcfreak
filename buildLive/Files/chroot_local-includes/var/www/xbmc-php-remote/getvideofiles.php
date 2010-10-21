<?php

include "topline.php";
include "config.php";

if(!empty($_GET['source']))
{

//get argument of the source
$location = $_GET['source'];

//json rpc call procedure
$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//array_sort function
function array_sort($a, $b) { return strnatcmp($a['label'], $b['label']); }

//get the results from the directory
$request2 = '{"jsonrpc" : "2.0", "method" : "Files.GetDirectory", "params" : { "directory" : "' . $location . '" }, "id" : 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $request2);
$array2 = json_decode(curl_exec($ch),true);

//query below contains both files and directories
$xbmcresults = $array2['result'];

//if the directory has content call Playlist.Add
if(!empty($_GET['directorycontent'])) {

  //get selected video
  $addplaylist = $_GET['directorycontent'];

  //clear video playlist
  $data = '{"jsonrpc": "2.0", "method": "VideoPlaylist.Clear", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
  $array = json_decode(curl_exec($ch),true);

  //add video to playlist
  $requestedfile = "$location$addplaylist";
  $request = '{"jsonrpc" : "2.0", "method": "VideoPlaylist.Add", "params" : { "file" : "' . $requestedfile . '" }, "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);

  //play item
  $playdata = '{"jsonrpc": "2.0", "method": "VideoPlaylist.Play", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $playdata);
  $array = json_decode(curl_exec($ch),true);
}

echo "<div id=\"utility\"><ul>";

//show directories
if (array_key_exists('directories', $xbmcresults)) {
  $directories = $xbmcresults['directories'];
  usort($directories, 'array_sort');
  foreach ($directories as $value)
  {
    $inhoud = $value['label'];
    $display = urlencode($value['file']);
    //remove synology eadir from results
    if (fnmatch("*eaDir*",$display,FNM_CASEFOLD)) { } else {
      echo "<li><a href=getvideofiles.php?source=$display>$inhoud</a></li>";
    }
  }
}

echo "</ul></div>";

echo "<div id=\"utility\"><ul>";

//show files in directory
if (array_key_exists('files', $xbmcresults)) {
  $files = $xbmcresults['files'];
  //sort on files name
  usort($files, 'array_sort');
  foreach ($files as $value)
  {
    $inhoud = $value['label'];
    $display = urlencode($value['file']);
    //make directory and video name url friendly
    $location2 = urlencode($location);
    $inhoud2 = urlencode($inhoud);
    echo "<li><a href=getvideofiles.php?source=$location2&directorycontent=$inhoud2>$inhoud</a></li>";
  }
}

echo "</ul></div>";

//show playlist url when videos are added
if(!empty($_GET['directorycontent'])) {
  echo "<br>";
  echo "<div id=\"utility\"><ul><li><a href=getplaylist.php>playlist</a></li></ul></div>";
}

} else { echo "No source given!"; }

include "downline.php";

?>
