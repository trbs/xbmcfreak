#!/bin/sh

xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

if [ ! -d "/home/$xbmcUser/.xbmc/userdata" ]; then
        mkdir /home/$xbmcUser/.xbmc/userdata
fi

if [ ! -f /home/$xbmcUser/.xbmc/userdata/advancedsettings.xml ] ; then
        cat > /home/$xbmcUser/.xbmc/userdata/advancedsettings.xml << 'EOF'
<advancedsettings>
 <video>
  <excludefromscan>
    <regexp>@eaDir</regexp>
    <regexp>@EADIR</regexp>
  </excludefromscan>
  <excludefromlisting>
    <regexp>@eaDir</regexp>
    <regexp>@EADIR</regexp>
  </excludefromlisting>
 </video>
</advancedsettings>
EOF
fi
chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

