#!/bin/sh

xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

mkdir -p /home/$xbmcUser/.xbmc/userdata &> /dev/null

if [ ! -f /home/$xbmcUser/.xbmc/userdata/RssFeeds.xml ] ; then
        cat > /home/$xbmcUser/.xbmc/userdata/RssFeeds.xml << EOF
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rssfeeds>
  <!-- RSS feeds. To have multiple feeds, just add a feed to the set. You can also have multiple sets.  !-->
  <!-- To use different sets in your skin, each must be called from skin with a unique id.              !-->
  <set id="1">
    <feed updateinterval="30">http://www.xbmcfreak.nl/feed/</feed>
  </set>
</rssfeeds>
EOF
fi
chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

