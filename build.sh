#!/bin/sh

#
# Depencency list: git-core apt-cacher-ng debootstrap asciidoc docbook-xsl curl build-essential
#

#
# Make sure only root can run our script
if [ "$(id -u)" != "0" ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi

# May be useful for debugging purposes
# KEEP_WORKAREA="yes"

# Clean our mess on exiting
cleanup()
{
	if [ -n "$WORKPATH" ]; then
		if [ -z "$KEEP_WORKAREA" ]; then
			echo "Cleaning workarea..." 
			rm -rf $WORKPATH
			if [ -f $THISDIR/binary.iso ]; then
				chmod 777 $THISDIR/binary.iso 
			fi
			echo "All clean"
		fi
	fi
}
trap 'cleanup' EXIT TERM INT

# Using apt-cacher(-ng) to speed up apt-get downloads
export APT_HTTP_PROXY="http://127.0.0.1:3142"
export APT_FTP_PROXY="http://127.0.0.1:3142"

# We use apt-cacher when retrieving d-i udebs, too
export http_proxy="http://127.0.0.1:3142"
export ftp_proxy="http://127.0.0.1:3142"

# Closest Ubuntu mirror
export UBUNTUMIRROR_BASEURL="http://ubuntu.apt-get.eu/ubuntu/"

THISDIR=$(pwd)
WORKDIR=workarea
WORKPATH=$THISDIR/$WORKDIR

if [ -d "$WORKPATH" ]; then
	rm -rf $WORKPATH
fi
mkdir $WORKPATH

# cp all (except svn directories) into workarea
rsync -r --exclude=.svn --exclude=$WORKDIR . $WORKDIR

if ! which lh > /dev/null ; then
	cd $WORKPATH/Tools
	git clone git://live.debian.net/git/live-helper.git
	if [ "$?" -ne "0" ]; then
		exit 1
	fi

	# Fix for missing directory for karmic d-i, to be removed when fixed upstream!
	cd live-helper/data/debian-cd
	ln -s lenny karmic

	LH_HOMEDIR=$WORKPATH/Tools/live-helper

	export LH_BASE="${LH_HOMEDIR}"
	export PATH="${PATH}:${LH_BASE}/helpers"

	cd $THISDIR
fi

#
# Build needed packages
#
cd $WORKPATH/buildDEBs
./build.sh
if [ "$?" -ne "0" ]; then
	exit 1
fi
cd $THISDIR

#
# Build binary drivers
#
cd $WORKPATH/buildBinaryDrivers
./build.sh
if [ "$?" -ne "0" ]; then
	exit 1
fi
cd $THISDIR

#
# Copy all needed files in place for the real build
#
mkdir -p $WORKPATH/buildLive/Files/chroot_local-packages &> /dev/null
mkdir -p $WORKPATH/buildLive/Files/binary_local-udebs &> /dev/null
mkdir -p $WORKPATH/buildLive/Files/binary_local-includes/live/restrictedDrivers &> /dev/null

if ! ls $WORKPATH/buildDEBs/live-initramfs*.* > /dev/null 2>&1; then
        echo "Files missing (1), exiting..."
        exit 1
fi
cp $WORKPATH/buildDEBs/live-initramfs*.* $WORKPATH/buildLive/Files/chroot_local-packages

if ! ls $WORKPATH/buildDEBs/squashfs-udeb*.* > /dev/null 2>&1; then
        echo "Files missing (2), exiting..."
        exit 1
fi
cp $WORKPATH/buildDEBs/squashfs-udeb*.* $WORKPATH/buildLive/Files/binary_local-udebs

if ! ls $WORKPATH/buildDEBs/live-installer*.* > /dev/null 2>&1; then
        echo "Files missing (3), exiting..."
        exit 1
fi
cp $WORKPATH/buildDEBs/live-installer*.* $WORKPATH/buildLive/Files/binary_local-udebs

if ! ls $WORKPATH/buildDEBs/xbmclive-installhelpers*.* > /dev/null 2>&1; then
        echo "Files missing (4), exiting..."
        exit 1
fi
cp $WORKPATH/buildDEBs/xbmclive-installhelpers*.* $WORKPATH/buildLive/Files/binary_local-udebs

if ! ls $WORKPATH/buildBinaryDrivers/*.ext3 > /dev/null 2>&1; then
        echo "Files missing (5), exiting..."
        exit 1
fi
cp $WORKPATH/buildBinaryDrivers/*.ext3 $WORKPATH/buildLive/Files/binary_local-includes/live/restrictedDrivers

#
# Perform XBMCLive image build
#
cd $WORKPATH/buildLive
./build.sh
cd $THISDIR

mv $WORKPATH/buildLive/binary.iso .
chmod 777 *.iso
