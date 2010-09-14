#!/bin/sh

xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

mkdir -p /home/$xbmcUser/.xbmc/userdata &> /dev/null

if [ ! -f /home/$xbmcUser/.xbmc/userdata/upnpserver.xml ] ; then
        cat > /home/$xbmcUser/.xbmc/userdata/upnpserver.xml << EOF
<upnpserver>
    <UUID>2bd1ab8e-7d95-1d13-9b1f-70905aafea00</UUID>
    <Port>53765</Port>
    <MaxReturnedItems>200</MaxReturnedItems>
    <UUIDRenderer>d2d9862c-0c21-9c9a-1343-08149b204711</UUIDRenderer>
    <PortRenderer>58841</PortRenderer>
</upnpserver>
EOF
fi
