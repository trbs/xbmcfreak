#!/bin/bash
#get current user
xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

#create download dir
if [ ! -d "/home/$xbmcUser/Downloads" ]; then
        mkdir /home/$xbmcUser/Downloads
        chmod 755 /home/$xbmcUser/Downloads
fi

#configure torrent-transmission
sed -i "s/USER=debian-transmission/USER=$xbmcUser/g" /etc/init.d/transmission-daemon
chown -hR $xbmcUser:$xbmcUser /var/lib/transmission-daemon

#configure samba
sed -i "s/home\/xbmc/home\/$xbmcUser/g" /etc/samba/smb.conf
service smbd restart

#mt-daapd
sed -i "s/home\/xbmc/home\/$xbmcUser/g" /etc/mt-daapd.conf
update-rc.d avahi-daemon defaults

#sabnzbd
sed -i "s/USER=xbmc/USER=$xbmcUser/g" /etc/default/sabnzbdplus
chown $xbmcUser:$xbmcUser /home/$xbmcUser/ -R
service sabnzbdplus restart

#makemkv
chmod 777 /usr/bin/makemkv
chmod 777 /usr/bin/makemkvcon
chown $xbmcUser:$xbmcUser /usr/bin/makemkv -R
chown $xbmcUser:$xbmcUser /usr/bin/makemkvcon -R

#user rights rtmpdump
chown $xbmcUser:$xbmcUser /usr/local/bin/rtmpdump -R
chown $xbmcUser:$xbmcUser /usr/local/sbin/rtmp* -R

#wakeonlanconfig
update-rc.d -f wakeonlanconfig defaults
