#!/bin/bash

#get current xbmc user
xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

if [ ! -d "/etc/xbmc/xbmcfreak" ]; then

	#create xbmc userdata dir
	mkdir -p /home/$xbmcUser/.xbmc/userdata &> /dev/null

	#create download dir
	if [ ! -d "/home/$xbmcUser/Downloads" ]; then
		mkdir /home/$xbmcUser/Downloads
		chmod 755 /home/$xbmcUser/Downloads
	fi

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

	#configure torrent-transmission
	sed -i "s/USER=debian-transmission/USER=$xbmcUser/g" /etc/init.d/transmission-daemon
	rm -rf /var/lib/transmission-daemon/info &> /dev/null
	mkdir /var/lib/transmission-daemon/info &> /dev/null
	ln -s /etc/transmission-daemon/settings.json /var/lib/transmission-daemon &> /dev/null
	chown -R $xbmcUser:$xbmcUser /var/lib/transmission-daemon &> /dev/null
	service transmission-daemon restart >/dev/null 2>&1 &

	#configure samba
	sed -i "s/home\/xbmc/home\/$xbmcUser/g" /etc/samba/smb.conf
	service smbd restart >/dev/null 2>&1 &

	#mt-daapd
	sed -i "s/home\/xbmc/home\/$xbmcUser/g" /etc/mt-daapd.conf
	update-rc.d avahi-daemon defaults &> /dev/null
	service mt-daapd restart >/dev/null 2>&1 &

	#sabnzbd
	sed -i "s/USER=xbmc/USER=$xbmcUser/g" /etc/default/sabnzbdplus
	service sabnzbdplus restart &> /dev/null
	chown $xbmcUser:$xbmcUser /home/$xbmcUser/.sabnzbd -R

	#makemkv
	chmod 755 /usr/bin/makemkv
	chmod 755 /usr/bin/makemkvcon
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

	# Setup Webserver
	if [ ! -f /home/$xbmcUser/.xbmc/userdata/guisettings.xml ] ; then
        	cat > /home/$xbmcUser/.xbmc/userdata/guisettings.xml << EOF
<settings>
    <services>
        <esallinterfaces>false</esallinterfaces>
        <escontinuousdelay>25</escontinuousdelay>
        <esenabled>true</esenabled>
        <esinitialdelay>750</esinitialdelay>
        <esmaxclients>20</esmaxclients>
        <esport>9777</esport>
        <esportrange>10</esportrange>
        <upnprenderer>false</upnprenderer>
        <upnpserver>false</upnpserver>
        <webserver>true</webserver>
        <webserverpassword></webserverpassword>
        <webserverport>8090</webserverport>
        <webserverusername>xbmc</webserverusername>
        <webskin>webinterface.default</webskin>
        <zeroconf>true</zeroconf>
    </services>
</settings>
EOF
	else
		sed -i 's#<webserver>.*#<webserver>true</webserver>#' /home/$xbmcUser/.xbmc/userdata/guisettings.xml
		sed -i 's#<webserverport>.*#<webserverport>8090</webserverport>#' /home/$xbmcUser/.xbmc/userdata/guisettings.xml
	fi

	#fix permissions
	chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

	#create xbmcfreak check dir
	mkdir -p /etc/xbmc/xbmcfreak &> /dev/null
fi

#fix hostname error
if ! grep -i -q XBMCLive /etc/hosts ; then
        sed '/127.0.1.1/D' -i /etc/hosts
        echo '127.0.1.1       XBMCLive' >> /etc/hosts
fi

#set XBMCLive hostname
hostname XBMCLive

#enable resume USB remotes (enable all ports)
for device in `cat /proc/acpi/wakeup |awk '{ print $1 }'|grep US..`; do
 echo $device  > /proc/acpi/wakeup &> /dev/null
done

exit 0
