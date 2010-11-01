<?php

include "topline.php";
include "config.php";

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//if argument1 is set, clear playlist
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

//if argument2 is set, change or rewind song
if(!empty($_GET['argument2']))
{
  //get audio playlist
  $audioplaylistdata = '{"jsonrpc": "2.0", "method": "AudioPlaylist.GetItems", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $audioplaylistdata);
  $audioplaylistarray = json_decode(curl_exec($ch),true);
  $audioplaylistresults = $audioplaylistarray['result'];

  //get selected song
  $selectedsong = substr($_GET['argument2'], 4);
  if ($selectedsong == $audioplaylistresults[current])
  {
    //current playing song is selected, do audio playlist rewind
    $data = '{"jsonrpc": "2.0", "method": "AudioPlayer.Rewind", "id": 1}';
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    $array = json_decode(curl_exec($ch),true);
  } else {
    //audio playlist next
    $data = '{"jsonrpc": "2.0", "method": "AudioPlaylist.Play", "params": ' . $selectedsong . ', "id": 1}';
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    $array = json_decode(curl_exec($ch),true);
  }
}

//get audio playlist
$audioplaylistdata = '{"jsonrpc": "2.0", "method": "AudioPlaylist.GetItems", "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $audioplaylistdata);
$audioplaylistarray = json_decode(curl_exec($ch),true);
$audioplaylistresults = $audioplaylistarray['result'];

//only show audio playlist if audio playlist is filled
if (!empty($audioplaylistresults[items]))
{

  //show Audio header
  echo "<div id=\"content\"><p>";
  echo "<b>Audio Playlist:</b><br>";
  echo "</p></div>";

  //show audio playlist
  echo "<div id=\"utility\"><ul>";

  if (array_key_exists('items', $audioplaylistresults))
  {
    //get results of playlist
    $results = $audioplaylistresults['items'];

    //count the number of songs in the selection
    $songcount = count($results);

    //put count on zero
    $i = 0;

    foreach ($results as $value)
    {
      //show music files in playlist where argument2 is songid in playlist
      $inhoud = $value['file'];
      if ($i == $audioplaylistresults[current] )
      {
        echo "<li><a style=\"color: #800000\" href=getplaylist.php?argument2=song$i>$inhoud</a></li>\n";
      }
      else
      {
        echo "<li><a href=getplaylist.php?argument2=song$i>$inhoud</a></li>\n";
      }
      $i++;
    }
  }
  echo "</ul></div>";
}

//break
echo "<br>";

//Get video playlist
$videoplaylistdata = '{"jsonrpc": "2.0", "method": "VideoPlaylist.GetItems", "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $videoplaylistdata);
$videoplaylistarray = json_decode(curl_exec($ch),true);
$videoplaylistresults = $videoplaylistarray['result'];

//only show video playlist if video playlist is filled
if (!empty($videoplaylistresults[items]))
{

  //show video header
  echo "<div id=\"utility\"><ul>";
  echo "<div id=\"content\"><p>";
  echo "<b>Video Playlist:</b><br>";
  echo "</p></div>";

  //show video play list items
  if (array_key_exists('items', $videoplaylistresults))
  {
    $results = $videoplaylistresults['items'];
    foreach ($results as $value)
    {
      $inhoud = $value['file'];
      echo "<li><a href=getplaylist.php?argument2=dosomething>$inhoud</a></li>\n";
    }
  }
  echo "</ul></div>";
}

//show button clear audio playlist
echo "<br>";
echo "<div id=\"utility\"><ul>";
echo "<li><a href=getplaylist.php?argument1=clearplaylist>Clear all Playlists</a></li>\n";
echo "</ul></div><br><br>";

include "downline.php";

?>
