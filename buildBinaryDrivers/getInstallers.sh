
retrieveLatestNVIDIAURL()
{
	# Something like:
	# http://us.download.nvidia.com/XFree86/Linux-x86/190.42/NVIDIA-Linux-x86-190.42-pkg1.run

	driverDownloadURL="http://download.nvidia.com/XFree86/Linux-x86/190.53/NVIDIA-Linux-x86-190.53-pkg1.run"
	echo $driverDownloadURL
}

getInstallers()
{
	#
	# Download the latest drivers installers
	#

	# Remove previous NVIDIA installer
	[ ! -f Files/chroot_local-includes/root/NVIDIA*.run ] || rm Files/chroot_local-includes/root/NVIDIA*.run

	# NVIDIA
	driverDownloadURL=$(retrieveLatestNVIDIAURL)

	echo "Downloading NVIDIA Installer from $driverDownloadURL ..."
	wget -nc --no-proxy -q $driverDownloadURL
	if [ "$?" -ne "0" ]; then
		echo "Error retrieving NVIDIA drivers, exiting..."
		exit 1
	fi

	mv NVIDIA*.run Files/chroot_local-includes/root

}
