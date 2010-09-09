#!/bin/bash
sed -i "s/hiddev/hidraw/g" /lib/udev/rules.d/70-hid2hci.rules
