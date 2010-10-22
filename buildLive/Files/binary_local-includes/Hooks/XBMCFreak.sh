#!/bin/bash

#get current xbmc user
xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

#create xbmc userdata dir
mkdir -p /home/$xbmcUser/.xbmc/userdata &> /dev/null

#create download dir
if [ ! -d "/home/$xbmcUser/Downloads" ]; then
mkdir /home/$xbmcUser/Downloads
	chmod 755 /home/$xbmcUser/Downloads
fi

#create user dirs
if [ ! -d "/home/$xbmcUser/Music" ]; then
	mkdir /home/$xbmcUser/Music
	chmod 755 /home/$xbmcUser/Music
fi

if [ ! -d "/home/$xbmcUser/Pictures" ]; then
	mkdir /home/$xbmcUser/Pictures
	chmod 755 /home/$xbmcUser/Pictures
fi

if [ ! -d "/home/$xbmcUser/TV Shows" ]; then
	mkdir "/home/$xbmcUser/TV Shows"
	chmod 755 "/home/$xbmcUser/TV Shows"
fi

if [ ! -d "/home/$xbmcUser/Videos" ]; then
	mkdir /home/$xbmcUser/Videos
	chmod 755 /home/$xbmcUser/Videos
fi

#xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

mkdir -p /home/$xbmcUser/.xbmc/userdata &> /dev/null

if [ ! -f /home/$xbmcUser/.xbmc/userdata/sources.xml ] ; then
        cat > /home/$xbmcUser/.xbmc/userdata/sources.xml << EOF
<sources>
    <video>
        <default pathversion="1"></default>
        <source>
            <name>Videos</name>
            <path pathversion="1">/home/$xbmcUser/Videos/</path>
        </source>
        <source>
            <name>TV Shows</name>
            <path pathversion="1">/home/$xbmcUser/TV Shows/</path>
        </source>
    </video>
    <music>
        <default pathversion="1"></default>
        <source>
            <name>Music</name>
            <path pathversion="1">/home/$xbmcUser/Music/</path>
        </source>
    </music>
    <pictures>
        <default pathversion="1"></default>
        <source>
            <name>Music</name>
            <path pathversion="1">/home/$xbmcUser/Pictures/</path>
        </source>
    </pictures>
</sources>
EOF
fi
chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

#exclude eadir
if [ ! -f /home/$xbmcUser/.xbmc/userdata/advancedsettings.xml ] ; then
        cat > /home/$xbmcUser/.xbmc/userdata/advancedsettings.xml << EOF
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
  <audio>
    <excludefromscan>
      <regexp>@eaDir</regexp>
      <regexp>@EADIR</regexp>
    </excludefromscan>
    <excludefromlisting>
      <regexp>@eaDir</regexp>
      <regexp>@EADIR</regexp>
    </excludefromlisting>
  </audio>
</advancedsettings>
EOF
fi
chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

#rrs feed
rm -rf /home/$xbmcUser/.xbmc/userdata/RssFeeds.xml

if [ ! -f /home/$xbmcUser/.xbmc/userdata/RssFeeds.xml ] ; then
	cat > /home/$xbmcUser/.xbmc/userdata/RssFeeds.xml << EOF
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<rssfeeds>
  <!-- RSS feeds. To have multiple feeds, just add a feed to the set. You can also have multiple sets. !-->
  <!-- To use different sets in your skin, each must be called from skin with a unique id. !-->
  <set id="1">
    <feed updateinterval="30">http://www.xbmcfreak.nl/feed/</feed>
  </set>
</rssfeeds>
EOF
fi
chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

#upnpserver
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
chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

#configure torrent-transmission
sed -i "s/USER=debian-transmission/USER=$xbmcUser/g" /etc/init.d/transmission-daemon
rm -rf /var/lib/transmission-daemon/info &> /dev/null
mkdir /var/lib/transmission-daemon/info &> /dev/null
ln -s /etc/transmission-daemon/settings.json settings.json &> /dev/null
chown -R $xbmcUser:$xbmcUser /var/lib/transmission-daemon &> /dev/null
service transmission-daemon restart >/dev/null 2>&1 &

#configure samba
sed -i "s/home\/xbmc/home\/$xbmcUser/g" /etc/samba/smb.conf
service smbd restart >/dev/null 2>&1 &

#mt-daapd
sed -i "s/home\/xbmc/home\/$xbmcUser/g" /etc/mt-daapd.conf
update-rc.d avahi-daemon defaults
service mt-daapd restart >/dev/null 2>&1 &

#sabnzbd
sed -i "s/USER=xbmc/USER=$xbmcUser/g" /etc/default/sabnzbdplus
service sabnzbdplus restart &> /dev/null
chown $xbmcUser:$xbmcUser /home/$xbmcUser/ -R

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

#logitech dinovo edge
sed -i "s/hiddev/hidraw/g" /lib/udev/rules.d/70-hid2hci.rules

#apache2
#echo "127.0.0.1 localhost XBMCLive" > /etc/hostname
#echo "127.0.1.1 XBMCLive" >> /etc/hostname
echo "ServerName XBMCLive" >> /etc/apache2/apache2.conf
service apache2 restart >/dev/null 2>&1 &

#fix ssh slowdown for some users
echo "UseDNS no" >> /etc/ssh/sshd_config
echo "GSSAPIAuthentication no" >> /etc/ssh/sshd_config
service ssh restart >/dev/null 2>&1 &

chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc
