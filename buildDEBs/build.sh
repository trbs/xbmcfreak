#!/bin/sh

#
# rationale for squashfs-udeb: 
# karmic d-i does not include squashfs module, we need one!
# Lucid has been fixed already
# https://bugs.launchpad.net/ubuntu/+source/linux/+bug/352615
#
# This is a quick hack to get the installer work on karmic right now, 
# hopefully the fix will be backported to karmic as well
#

THISDIR=$(pwd)
WORKDIR="workarea"

getPackage()
{
	udebListURL="http://archive.ubuntu.com/ubuntu/dists/karmic/main/installer-i386/current/images/udeb.list"

	tmpFile=$(mktemp -q)
	curl -x "" -s -f -o $tmpFile $udebListURL
	if [ "$?" -ne "0" ]; then
		echo "Installer udeb list not found, exiting..."
		exit 1
	fi

	# fs-core-modules-2.6.31-14-generic-di 2.6.31-14.48 i386
	kernelVersion="$(cat $tmpFile | grep fs-core | awk '{ print $2 }')"
	if [ -z "$kernelVersion" ]; then
		echo "Installer kernel version not found, exiting..."
		exit 1
	fi

	# linux-image-2.6.31-14-generic_2.6.31-14.48_i386.deb
	packageName=linux-image-$(echo $kernelVersion | awk -F'.' '{ print $1"."$2"."$3}')-generic_"$kernelVersion"_i386.deb

	packageURL="http://archive.ubuntu.com/ubuntu/pool/main/l/linux/$packageName"

	wget -q $packageURL
	if [ "$?" -ne "0" ] || [ ! -f "$packageName" ] ; then
		echo "Needed kernel not found, exiting..."
		exit 1
	fi
	rm $tmpFile

	echo $packageName
}

extractModule()
{
	if [ -d $WORKDIR ]; then
		rm -rf $WORKDIR 
	fi
	mkdir $WORKDIR

	# Extract package
	dpkg -x $1 $WORKDIR

	# Get file from package
	modulesDir=$(ls $WORKDIR/lib/modules/)
	mkdir -p $modulesDir/kernel/fs
	cp -R $WORKDIR/lib/modules/$modulesDir/kernel/fs/squashfs $modulesDir/kernel/fs

	# Remove any previous modules tree in the destination directory
	rm -rf $THISDIR/squashfs-udeb/modules/*

	# Copy the new tree in place
	mkdir $THISDIR/squashfs-udeb/modules
	mv $modulesDir $THISDIR/squashfs-udeb/modules

	# Cleanup
	rm $1
	rm -rf $WORKDIR 
}

if ! ls linux-image-*.deb > /dev/null 2>&1 ; then
	# Get matching package
	echo "Selecting and downloading the kernel package..."
	packageName=$(getPackage)
	if [ ! -f "$packageName" ]; then
		echo "Error retrieving installer kernel, exiting..."
		exit 1
	fi

	echo "Extracting files..."
	extractModule $packageName
fi

if ! ls squashfs-udeb_*.udeb > /dev/null 2>&1 ; then
	echo "Making squashfs-udeb..."
	cd $THISDIR/squashfs-udeb
	dpkg-buildpackage -rfakeroot -b -uc -us 
	cd $THISDIR
fi

if ! ls xbmclive-installhelpers_*.udeb > /dev/null 2>&1 ; then
	echo "Making xbmclive-installhelpers..."
	cd $THISDIR/xbmclive-installhelpers
	dpkg-buildpackage -rfakeroot -b -uc -us 
	cd $THISDIR
fi

if ! ls live-initramfs_*.udeb > /dev/null 2>&1 ; then
	echo "Making live-initramfs..."
	cd $THISDIR/live-initramfs-ubuntu
	dpkg-buildpackage -rfakeroot -b -uc -us 
	cd $THISDIR
fi

# Retrieve live_installer from Debian's repositories
# TODO identify & retrieve the latest!
if ! ls live-installer*.udeb > /dev/null 2>&1 ; then
	echo "Retrieving live_installer udebs..."
	wget -q "http://ftp.uk.debian.org/debian/pool/main/l/live-installer/live-installer_13_i386.udeb"
	if [ "$?" -ne "0" ] || [ ! -f live-installer_13_i386.udeb ] ; then
		echo "Needed package (1) not found, exiting..."
		exit 1
	fi
fi
