
retrieveLatestNVIDIAURL()
{
	# Something like:
	# http://us.download.nvidia.com/XFree86/Linux-x86/190.42/NVIDIA-Linux-x86-190.42-pkg1.run

	driverDownloadURL="http://download.nvidia.com/XFree86/Linux-x86/190.53/NVIDIA-Linux-x86-190.53-pkg1.run"
	echo $driverDownloadURL
}

getNvidiaInstallers()
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

retrieveLatestAMDURL()
{
        # Something like:
        # https://a248.e.akamai.net/f/674/9206/0/www2.ati.com/drivers/linux/ati-driver-installer-9-11-x86.x86_64.run

        tmpFile=$(mktemp -q)

        curl -x "" -f -s -o $tmpFile "http://support.amd.com/us/gpudownload/linux/Pages/radeon_linux.aspx?type=2.4.1&product=2.4.1.3.42&lang=English"
        if [ "$?" -ne "0" ]; then
                echo "AMD driver page not found, exiting..."
                exit 1
        fi

        #<a class="submitButton" href="https://a248.e.akamai.net/f/674/9206/0/www2.ati.com/drivers/linux/ati-driver-installer-9-11-x86.x86_64.run">Download</a>

        driverDownloadURL=$(cat $tmpFile | grep -o -e "class=\"submitButton\" href=\"\([^\"]\+\?\)\">Download</a>")
        driverDownloadURL=$(echo $driverDownloadURL | sed -e "s/.*href=\"\([^\"]*\)\".*/\1/")

        if [ -z "$driverDownloadURL" ]; then
                echo "AMD driver URL not found, exiting..."
                exit 1
        fi
        rm $tmpFile

        echo $driverDownloadURL
}

getBCDriversSources()
{
        # Get Broadcom CristalHD main tree

        # Remove previous Broadcom file
        [ ! -f Files/chroot_local-includes/root/crystalhd*.gz ] || rm Files/chroot_local-includes/root/crystalhd*.gz

        echo "Downloading Broadcom drivers snapshot from http://git.wilsonet.com/crystalhd.git ..."
        wget -nc --no-proxy -q "http://git.wilsonet.com/crystalhd.git?a=snapshot;h=HEAD;sf=tgz" -O crystalhd-HEAD.tar.gz
        if [ ! -f crystalhd-HEAD.tar.gz ]; then
                echo "Error retrieving Broadcom drivers, exiting..."
                exit 1
        fi

        cp crystalhd-HEAD.tar.gz Files/chroot_local-includes/root
}

getAMDInstaller()
{
        # Remove previous AMD installer
        [ ! -f Files/chroot_local-includes/root/ati*.run ] || rm Files/chroot_local-includes/root/ati*.run

        # AMD
        driverDownloadURL=$(retrieveLatestAMDURL)

        echo "Downloading AMD Installer from $driverDownloadURL ..."
        wget -nc --no-proxy -q $driverDownloadURL
        if ! ls ati*.run  > /dev/null 2>&1 ; then
                echo "Error retrieving ATI drivers, exiting..."
                exit 1
        fi

        mv ati*.run Files/chroot_local-includes/root
}

