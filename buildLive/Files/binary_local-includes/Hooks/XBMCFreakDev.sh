#!/bin/bash
xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

#look for dev machine
if ifconfig eth0 | grep '00:01:2e:bc:12:bc' > /dev/null; then

#
# Create directories for XBMC sources
#

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

#create download dir
if [ ! -d "/home/$xbmcUser/Downloads" ]; then
        mkdir /home/$xbmcUser/Downloads
        chmod 755 /home/$xbmcUser/Downloads
fi

mkdir -p /home/$xbmcUser/.xbmc/userdata &> /dev/null

#copy guisettings.xml
cp /usr/share/xbmc/dev/guisettings-dev.xml /home/$xbmcUser/.xbmc/userdata/guisettings.xml -Rf
chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc

#nfs shares
apt-get update
aptitude -y install nfs-common
echo "192.168.0.111:/volume1/misc/Videos /home/xbmc/Videos nfs defaults 0 0" >> /etc/fstab
echo "192.168.0.111:/volume1/misc/Music /home/xbmc/Music nfs defaults 0 0" >> /etc/fstab
echo "192.168.0.111:/volume1/misc/Pictures /home/xbmc/Pictures nfs defaults 0 0" >> /etc/fstab
echo "192.168.0.111:/volume1/misc/TV Shows /home/xbmc/TV Shows nfs defaults 0 0" | sed -e "s/TV Shows/TV\\\040Shows/g" >> /etc/fstab
echo "192.168.0.111:/volume1/downloads /home/xbmc/Downloads nfs defaults 0 0" >> /etc/fstab
mount -a

else
echo "Not Found"
fi
