#!/bin/bash

THISDIR=$(pwd)
WORKDIR=workarea

. $THISDIR/getInstallers.sh
. $THISDIR/mkConfig.sh

# USE_LOCAL_INSTALLERS="yes"

build()
{
	cd $THISDIR/$WORKDIR

	lh bootstrap
	lh chroot

	# safeguard against crashes
	lh chroot_devpts remove
	lh chroot_proc remove
	lh chroot_sysfs remove
	
	for modulesdir in chroot/lib/modules/*
	do
		umount $modulesdir/volatile &> /dev/null
	done

	cd $THISDIR
}

if ! which lh > /dev/null ; then
	echo "A required package (live-helper) is not available, exiting..."
	exit 1
fi

mkdir -p Files/chroot_local-includes/root &> /dev/null

# Get Nvidia installers 
if [ -z "$USE_LOCAL_INSTALLERS" ]; then
	rm *.run &> /dev/null
	getNvidiaInstallers
else
	mv NVIDIA*.run Files/chroot_local-includes/root
fi

# Clean any previous run
rm -rf *.ext3 &> /dev/null

rm -rf $WORKDIR &> /dev/null
mkdir -p "$THISDIR/$WORKDIR"
cd "$THISDIR/$WORKDIR"

# Create config tree
makeConfig

# Create chroot and build drivers
build

# Get files from chroot
cp $WORKDIR/chroot/tmp/*.ext3 . &> /dev/null
cp $WORKDIR/chroot/tmp/crystalhd.tar . &> /dev/null
