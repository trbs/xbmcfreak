<?php

include "config.php";
include "topline.php";

//artist argument should be filled in
if(!empty($_GET['artist']))
{

  //get artist and artistid arguments
  $artist = $_GET['artist'];
  $artistid = $_GET['artistid'];

  //curl init
  $ch = curl_init();
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  curl_setopt($ch, CURLOPT_POST, 1);
  curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

  //prepare the field values being posted to the service
  $data = '{"jsonrpc": "2.0", "method": "AudioLibrary.GetAlbums", "params": {"artistid": ' . $artistid . '}, "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
  $array = json_decode(curl_exec($ch),true);
  $results = $array['result'];

  //show navigation bar
  echo "<div id=\"utility\"><ul><li><a href=getartists.php>Artists</a></li>";
  $urlartist = urlencode($artist);
  echo "<li><a href=getalbums.php?artist=$urlartist&artistid=$artistid>$artist</a></li></ul></div>";

  //show all albums
  echo "<div id=\"utility\"><ul>";
  $artists = $results['albums'];
  foreach ($artists as $value)
  {
    $album =  $value['label'];
    $albumid = $value['albumid'];
    $urlalbum = urlencode($album);
    $urlartist = urlencode($artist);
    echo "<li><a href=getsongs.php?artist=$urlartist&artistid=$artistid&album=$urlalbum&albumid=$albumid>$artist - $album</a></li>";
  }

  echo "</ul></div>";
}

else

{
  echo "Artist not given";
}

include "downline.php";

?>


