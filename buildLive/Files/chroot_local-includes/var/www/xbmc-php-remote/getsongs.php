<?php
include "topline.php";
include "config.php";

if(!empty($_GET['artist'])) {

//get and set arguments
$album = $_GET['album'];
$albumid = $_GET['albumid'];
$artist = $_GET['artist'];
$artistid = $_GET['artistid'];
$playsong = $_GET['requestedsong'];

//show errors
ini_set('display_errors', 1);
error_reporting(-1);

//json rpc call
$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//prepare the field values being posted to the service and get results
$data = '{"jsonrpc": "2.0", "method": "AudioLibrary.GetSongs", "params": {"albumid": ' . $albumid . '}, "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
$array = json_decode(curl_exec($ch),true);
$results = $array['result'];

echo "<div id=\"utility\"><ul>";

//show naviation bar
if ($_GET['artist'] = 'unknown')
{
  echo "<li><a href=getalbumsgeneric.php>Albums</a></li>";
}
else
{
  echo "<li><a href=getartists.php>Artists</a></li>";
  $urlartist = urlencode($artist);
  echo "<li><a href=getalbums.php?artist=$urlartist&artistid=$artistid>$artist</a></li>";
  $urlalbum = urlencode($album);
  echo "<li><a href=getsongs.php?artist=$urlartist&artistid=$artistid&album=$urlalbum&albumid=$albumid>$album</a></li>";
}

echo "</ul></div>";

//array_sort function
function array_sort($a, $b) { return strnatcmp($a['label'], $b['label']); }

//check if argument is not empty
if(!empty($_GET['requestedsong'])) {

  //get only the songs from the array
  $songs = $results['songs'];

  //sort songs on name
  usort($songs, 'array_sort');

  //count the number of songs in the selection
  $songcount = count($results['songs']);

  //put count on zero
  $i = 0;

  //search the arraykey for the selected song
  foreach ($songs as $value)
  {
    $songid = $value['songid'];
    $song = $value['label'];
    //here's a match
    if ($playsong == $songid)
    {
      //put the number of remaining songs in a queue
      $songqueue = $songcount - $i;

      //we still need i, define new var
      $y = $i;

      //clear playlist
      $data = '{"jsonrpc": "2.0", "method": "AudioPlaylist.Clear", "id": 1}';
      curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
      $array = json_decode(curl_exec($ch),true);

      //get remaining songs from queue
      while ($y <= $songcount -1)
        {
          //get details for each song
          $arraysongs = $songs[$y];
          $songlocations = $arraysongs['file'];

          //add songs to playlist
          $dataplaylist = '{"jsonrpc" : "2.0", "method": "AudioPlaylist.Add", "params": { "file" : "' . $songlocations . '"}, "id": 1}';
          curl_setopt($ch, CURLOPT_POSTFIELDS, $dataplaylist);
          $array = json_decode(curl_exec($ch),true);

          //raise number for loop remaining songs
          $y++;
        }

      //play item
      $playdata = '{"jsonrpc": "2.0", "method": "AudioPlaylist.Play", "id": 1}';
      curl_setopt($ch, CURLOPT_POSTFIELDS, $playdata);
      $array = json_decode(curl_exec($ch),true);

      }
    //raise number for loop find array_key
    $i++;
  }
//end for argument not empty
}

//show results on the screen
echo "<div id=\"utility\"><ul>";

$songs = $results['songs'];
usort($songs, 'array_sort');
foreach ($songs as $value)
{
  $song =  $value['label'];
  $songid = $value['songid'];
  $urlsong = urlencode($song);
  $urlartist = urlencode($artist);
  $urlalbum = urlencode($album);
  echo "<li><a href=getsongs.php?artist=$urlartist&artistid=$artistid&album=$urlalbum&albumid=$albumid&requestedsong=$songid>$song</a></li>";
}

echo "</ul></div>";

} else { echo "No artist given!"; }

echo "<br><div id=\"utility\"><ul><li><a href=getplaylist.php>Playlist</a></li></ul></div>";

include "downline.php";
?>

