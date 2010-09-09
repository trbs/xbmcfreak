#!/bin/bash

xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

NvidiaHDMI=$(lspci -nn | grep 'Audio' | grep '10de:0be3')

if [ ! -n "$NvidiaHDMI" ] ; then
        exit 0
fi

if [ ! -f /home/$xbmcUser/.asoundrc ] ; then
	cat > /home/$xbmcUser/.asoundrc << 'EOF'
pcm.!default {
        type plug
        slave {
                pcm "both"
        }
}
pcm.both {
        type route
        slave {
                pcm multi
                channels 4
        }
        ttable.0.0 1.0
        ttable.1.1 1.0
        ttable.0.2 1.0
        ttable.1.3 1.0
}
pcm.multi {
        type multi
        slaves.a {
                pcm "tv"
                channels 2
        }
        slaves.b {
                pcm "dmixrec"
                channels 2
        }
        bindings.0.slave a
        bindings.0.channel 0
        bindings.1.slave a
        bindings.1.channel 1
        bindings.2.slave b
        bindings.2.channel 0
        bindings.3.slave b
        bindings.3.channel 1
}
pcm.dmixrec {
    type dmix
    ipc_key 1024
    slave {
        pcm "receiver"
        period_time 0
        period_size 1024
        buffer_size 8192
        rate 48000
     }
     bindings {
        0 0
        1 1
     }
}
pcm.tv {
        type hw
        =HDMICARD=
        =HDMIDEVICE=
        channels 2
}
pcm.receiver {
        type hw
        =DIGITALCARD=
        =DIGITALDEVICE=
        channels 2
}
EOF
fi

HDMICARD=`aplay -l | grep 'NVIDIA HDMI' | awk -F: '{ print $1 }' | awk '{ print $2 }'`
HDMIDEVICE=`aplay -l | grep 'NVIDIA HDMI' | awk -F: '{ print $2 }' | awk '{ print $5 }'`

DIGITALCARD=`aplay -l | grep 'ALC888 Digital' | awk -F: '{ print $1 }' | awk '{ print $2 }'`
DIGITALDEVICE=`aplay -l | grep 'ALC888 Digital' | awk -F: '{ print $2 }' | awk '{ print $5 }'`

sed -i "s/=HDMICARD=/card $HDMICARD/g" /home/$xbmcUser/.asoundrc
sed -i "s/=HDMIDEVICE=/device $HDMIDEVICE/g" /home/$xbmcUser/.asoundrc

sed -i "s/=DIGITALCARD=/card $DIGITALCARD/g" /home/$xbmcUser/.asoundrc
sed -i "s/=DIGITALDEVICE=/device $DIGITALDEVICE/g" /home/$xbmcUser/.asoundrc

#unmute alsa
/usr/bin/amixer -q -c 0 sset 'IEC958 Default PCM',0 unmute > /dev/null
/usr/bin/amixer -q -c 0 sset 'IEC958',0 unmute > /dev/null
/usr/bin/amixer -q -c 0 sset 'IEC958',1 unmute > /dev/null

chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.asoundrc