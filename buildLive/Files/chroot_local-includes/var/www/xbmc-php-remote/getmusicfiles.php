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

//if the directory has content call AudioPlaylist.Add
if(!empty($_GET['directorycontent'])) {

  //get selected songs
  $addplaylist = $_GET['directorycontent'];

  //only the files
  $files = $xbmcresults['files'];

  //sort files on name
  usort($files, 'array_sort');

  //count the number of songs
  $songcount = count($files);

  //put counter on zero
  $i = 0;

  //search the array_key of the selected song
  foreach ($files as $value)
  {
    $song = $value['label'];
    //there's a match
    if ($song == $addplaylist)
    {
      //count remaining songs
      $songqueue = $songcount - $i;

      //we still need i
      $y = $i;

      //clear playlist
      $data = '{"jsonrpc": "2.0", "method": "AudioPlaylist.Clear", "id": 1}';
      curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
      $array = json_decode(curl_exec($ch),true);

      //get remaining songs from the array
      while ($y <= $songcount -1)
        {
          //get the location of every song
          $arraysongs = $files[$y];
          $songlocations = $arraysongs['file'];

          //filter on .mp3
          if (fnmatch("*.mp3",$songlocations,FNM_CASEFOLD))
          {
            //add song to playlist
            $request = '{"jsonrpc" : "2.0", "method": "AudioPlaylist.Add", "params" : { "file" : "' . $songlocations . '"}, "id": 1}';
            curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
            $array = json_decode(curl_exec($ch),true);
          }
          //loop for remaining songs
          $y++;
        }

      //play item
      $playdata = '{"jsonrpc": "2.0", "method": "AudioPlaylist.Play", "id": 1}';
      curl_setopt($ch, CURLOPT_POSTFIELDS, $playdata);
      $array = json_decode(curl_exec($ch),true);

      }
    //loop for array_key
    $i++;
  }
//end for argument empty
}

echo "<div id=\"utility\"><ul>";

//show directories
if (array_key_exists('directories', $xbmcresults)) {
  $directories = $xbmcresults['directories'];
  //sort directories
  usort($directories, 'array_sort');
  foreach ($directories as $value)
  {
    $inhoud = $value['label'];
    $display = urlencode($value['file']);
    //remove synology shares from result
    if (fnmatch("*eaDir*",$display,FNM_CASEFOLD)) { } else {
      echo "<li><a href=getmusicfiles.php?source=$display>$inhoud</a></li>";
    }
  }
}

echo "</ul></div>";

echo "<div id=\"utility\"><ul>";

//show files in directory
if (array_key_exists('files', $xbmcresults)) {
  $files = $xbmcresults['files'];
  //sort on name
  usort($files, 'array_sort');
  foreach ($files as $value)
  {
    $inhoud = $value['label'];
    $display = urlencode($value['file']);
    //make directory and mp3 name url friendly
    $location2 = urlencode($location);
    $inhoud2 = urlencode($inhoud);
    //show only .mp3 files
    if (fnmatch("*.mp3",$display,FNM_CASEFOLD)) {
      echo "<li><a href=getmusicfiles.php?source=$location2&directorycontent=$inhoud2>$inhoud</a></li>";
    }
  }
}

echo "</ul></div>";

//show playlist url when songs are added
if(!empty($_GET['directorycontent'])) {
  echo "<br>";
  echo "<div id=\"utility\"><ul><li><a href=getplaylist.php>Playlist</a></li></ul></div>";
}

} else { echo "No source given!"; }

include "downline.php";

?>
