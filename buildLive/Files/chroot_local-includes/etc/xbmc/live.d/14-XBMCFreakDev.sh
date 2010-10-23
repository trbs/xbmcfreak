#!/bin/bash
xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

#look for dev machine
if ifconfig eth0 | grep '00:01:2e:bc:12:bc' > /dev/null; then

	mkdir -p /home/$xbmcUser/.xbmc/userdata &> /dev/null

	#copy guisettings.xml
	cp /usr/share/xbmc/dev/guisettings-dev.xml /home/$xbmcUser/.xbmc/userdata/guisettings.xml -Rf
	chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

	if ! grep -i -q 192.168.0.111 /etc/fstab ; then
		#add nfs shares
		echo "192.168.0.111:/volume1/misc/Videos /home/xbmc/Videos nfs defaults 0 0" >> /etc/fstab
		echo "192.168.0.111:/volume1/misc/Music /home/xbmc/Music nfs defaults 0 0" >> /etc/fstab
		echo "192.168.0.111:/volume1/misc/Pictures /home/xbmc/Pictures nfs defaults 0 0" >> /etc/fstab
		echo "192.168.0.111:/volume1/misc/TV Shows /home/xbmc/TV Shows nfs defaults 0 0" | sed -e "s/TV Shows/TV\\\040Shows/g" >> /etc/fstab
		echo "192.168.0.111:/volume1/downloads /home/xbmc/Downloads nfs defaults 0 0" >> /etc/fstab
		chmod 755 /home/xbmc/Downloads
		chmod 755 /home/xbmc/Pictures
		chmod 755 /home/xbmc/Music
		chmod 755 /home/xbmc/Videos
		chmod 755 '/home/xbmc/TV Shows'
	fi
	mount -a 2>&1 &
else
	echo "XBMC Dev machine not found"
fi

exit 0
