<?php

include "topline.php";
include "config.php";

$ch = curl_init();
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_URL, $xbmcjsonservice);

//get active or inactive players
$request = '{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}';
curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
$array = json_decode(curl_exec($ch),true);
echo "<br>";

if(!empty($_GET['action'])) {

if ($_GET['action'] == 'AudioPlaylist.Play') {
  //prepare the field values being posted to the service
  $request = '{"jsonrpc": "2.0", "method": "AudioPlaylist.Play", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);
}

if ($_GET['action'] == 'AudioPlaylist.SkipPrevious') {
  //audio skip previous
  $request = '{"jsonrpc": "2.0", "method": "AudioPlaylist.SkipPrevious", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);

  //video skip previous
  $request = '{"jsonrpc": "2.0", "method": "VideoPlaylist.SkipPrevious", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);
}

if ($_GET['action'] == 'AudioPlaylist.SkipNext') {
  //audio skip next
  $request = '{"jsonrpc": "2.0", "method": "AudioPlaylist.SkipNext", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);

  //video skip next
  $request = '{"jsonrpc": "2.0", "method": "VideoPlaylist.SkipNext", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);
}

if ($_GET['action'] == 'AudioPlayer.PlayPause') {
  //audio play or pause
  $request = '{"jsonrpc": "2.0", "method": "AudioPlayer.PlayPause", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);

  //video play or pause
  $request = '{"jsonrpc": "2.0", "method": "VideoPlayer.PlayPause", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);
}

//Action Move up
if ($_GET['action'] == 'Action.Move.Up') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(3)", "r");
}

//Action Move down
if ($_GET['action'] == 'Action.Move.Down') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(4)", "r");
}

//Action Move left
if ($_GET['action'] == 'Action.Move.Left') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(1)", "r");
}

//Action Move right
if ($_GET['action'] == 'Action.Move.Right') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(2)", "r");
}

//Action Select
if ($_GET['action'] == 'Action.Select') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(7)", "r");
}

//Action Previous
if ($_GET['action'] == 'Action.Previous') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(10)", "r");
}

//Action Show Info
if ($_GET['action'] == 'Action.Show.Info') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(11)", "r");
}

//Action Show Info
if ($_GET['action'] == 'Action.Context') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(117)", "r");
}

//Action Show Info
if ($_GET['action'] == 'Action.Stop') {
  fopen("$xbmchttpapi/xbmcCmds/xbmcHttp?command=Action(13)", "r");
}

}

  //get current volume
  $request = '{"jsonrpc": "2.0", "method": "XBMC.GetVolume", "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);

  //increase and decrease volumes
  $decreasevolume = $array['result'] - 5;
  $increasevolume = $array['result'] + 5;

if(!empty($_GET['action'])) {

//incease volume
if ($_GET['action'] == 'Increase.Volume') {
  $request = '{"jsonrpc": "2.0", "method": "XBMC.SetVolume", "params": ' . $increasevolume . ', "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);
}

//decrease volume
if ($_GET['action'] == 'Decrease.Volume') {
  $request = '{"jsonrpc": "2.0", "method": "XBMC.SetVolume", "params": ' . $decreasevolume . ', "id": 1}';
  curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
  $array = json_decode(curl_exec($ch),true);
}

}

echo "<center>";
echo "<a href=remote.php?action=Action.Stop><img src=\"./img/media28-stop.png\"></a>\n";
echo "<a href=remote.php?action=Action.Move.Up><img src=\"./img/arrow3-up.png\"></a>\n";
echo "<a href=remote.php?action=Action.Context><img src=\"./img/letter-c.png\"></a><br>\n";

echo "<a href=remote.php?action=Action.Move.Left><img src=\"./img/arrow3-left.png\"></a>\n";
echo "<a href=remote.php?action=Action.Select><img src=\"./img/word-ok.png\"></a>\n";
echo "<a href=remote.php?action=Action.Move.Right><img src=\"./img/arrow3-right.png\"></a><br>\n";

echo "<a href=remote.php?action=Action.Previous><img src=\"./img/arrow-redo.png\"></a>\n";
echo "<a href=remote.php?action=Action.Move.Down><img src=\"./img/arrow3-down.png\"></a>\n";
echo "<a href=remote.php?action=Action.Show.Info><img src=\"./img/information.png\"></a><br><br>\n";
echo "</center>";

echo "<center>";

//TODO: play button when song is paused, paused button when song is playing.
//if (($array['result']['paused']) == 1) {echo "Song paused"; echo "<br><br>"; } else { echo "Playing"; echo "<br><br>"; }
echo "<a href=remote.php?action=AudioPlayer.PlayPause><img src=\"./img/play-pause-sign.png\"></a><br>\n";
echo "<a href=remote.php?action=Decrease.Volume><img src=\"./img/volume-left.png\"></a>\n";
echo "<a href=remote.php?action=AudioPlaylist.SkipPrevious><img src=\"./img/arrows-skip-backward.png\"></a>\n";
echo "<a href=remote.php?action=AudioPlaylist.SkipNext><img src=\"./img/arrows-skip-forward.png\"></a>\n";
echo "<a href=remote.php?action=Increase.Volume><img src=\"./img/volume-right.png\"></a><br>\n";

//show playlist button
echo "<br>";
echo "<div id=\"utility\"><ul>";
echo "<li><a href=getplaylist.php>Playlist</a></li>\n";
echo "</ul></div>";

echo "<center>";

include "downline.php";

?>
