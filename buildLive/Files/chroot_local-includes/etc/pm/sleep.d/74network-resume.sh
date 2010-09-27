#!bin/bash

. /usr/lib/pm-utils/functions

case "$1" in
        thaw|resume)
                /etc/init.d/networking restart
                ;;
        *)
                ;;

esac

exit $?
