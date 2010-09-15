#!/bin/sh

#      Copyright (C) 2005-2010 Team XBMC
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


cat > $WORKPATH/buildLive/Files/chroot_sources/pre-posed.list.chroot << EOF
deb http://ppa.launchpad.net/kernel-ppa/pre-proposed/ubuntu lucid main 
EOF

cat > $WORKPATH/buildLive/Files/chroot_sources/pre-posed.list.binary << EOF
deb http://ppa.launchpad.net/kernel-ppa/pre-proposed/ubuntu lucid main 
EOF

if [ ! -f $WORKPATH/pre-posed.key ] ; then
	wget --no-proxy -O $WORKPATH/pre-posed.html "http://keyserver.ubuntu.com:11371/pks/lookup?op=get&search=0x800AA67AE64A6D9E1859C561A8267963484B044F"
	if [ "$?" -ne "0" ] || [ ! -f $WORKPATH/pre-posed.html ] ; then
		echo "Needed keyfile not found, exiting..."
		exit 1
	fi

	#
	# Page structure:
	#
	# <html><head><title> ... </title></head>
	# <body><h1> ... </h1>
	# <pre>
	# -----BEGIN PGP PUBLIC KEY BLOCK-----
	# ...
	# -----END PGP PUBLIC KEY BLOCK-----
	# </pre>
	# </body></html>
	#

	# Filter out all before <pre> and after </pre>
	cat $WORKPATH/pre-posed.html | sed -e '1,/<pre>/d;/<\/pre>/,$d' > $WORKPATH/pre-posed.key
	rm $WORKPATH/pre-posed.html
fi

cp $WORKPATH/pre-posed.key $WORKPATH/buildLive/Files/chroot_sources/pre-posed.binary.gpg
cp $WORKPATH/pre-posed.key $WORKPATH/buildLive/Files/chroot_sources/pre-posed.chroot.gpg
rm $WORKPATH/pre-posed.key
