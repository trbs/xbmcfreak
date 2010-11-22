<!-- First, detect the iPhone or iPod useragent using PHP -->
<?php
if (ereg('iPhone',$_SERVER['HTTP_USER_AGENT'])) {
$iphone = 1;
}
elseif (ereg('iPod',$_SERVER['HTTP_USER_AGENT'])) {
$iphone = 1;
}
elseif (ereg('iPad',$_SERVER['HTTP_USER_AGENT'])) {
$iphone = 2;
}
else {
$iphone = 0;
}
?>

