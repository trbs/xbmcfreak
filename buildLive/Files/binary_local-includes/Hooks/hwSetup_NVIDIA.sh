#!/bin/bash

#      Copyright (C) 2005-2008 Team XBMC
#      http://www.xbmc.org
#
#  This Program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2, or (at your option)
#  any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with XBMC; see the file COPYING.  If not, write to
#  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
#  http://www.gnu.org/copyleft/gpl.html

#check Nvidia GPU
nvidiaGpuType=$(lspci -nn | grep '0300' | grep '10de')
if [ ! -n "$nvidiaGpuType" ] ; then
	exit 0
fi

xbmcUser=$(getent passwd 1000 | sed -e 's/\:.*//')

mkdir -p /home/$xbmcUser/.xbmc/userdata

if [ ! -f /home/$xbmcUser/.xbmc/userdata/advancedsettings.xml ] ; then
	cat > /home/$xbmcUser/.xbmc/userdata/advancedsettings.xml << 'EOF'
<advancedsettings>
    <cputempcommand>echo "$(sensors -u | tail -n4 | grep temp1_input | awk '{print $2 }' |awk '{printf("%d\n",$1 + 0.5);}') C"</cputempcommand>
    <gputempcommand>echo "$(nvidia-settings -tq gpuCoreTemp) C"</gputempcommand>
</advancedsettings>
EOF
fi

#
# Always sync to vblank
#
if [ ! -f /home/$xbmcUser/.xbmc/userdata/guisettings.xml ] ; then
	cat > /home/$xbmcUser/.xbmc/userdata/guisettings.xml << 'EOF'
<settings>
    <videoscreen>
        <vsync>2</vsync>
    </videoscreen>
</settings>
EOF
fi

chown -R $xbmcUser:$xbmcUser /home/$xbmcUser/.xbmc
