#!/bin/bash

echo "Deconz installer"

cd /tmp/
if [ -d "deconz" ]; then
    echo "Removing old Deconz installation"
    sudo rm -rf deconz
fi
mkdir deconz
cd deconz/

wget http://www.dresden-elektronik.de/rpi/deconz/beta/deconz-2.05.02-qt5.deb
sudo dpkg --install deconz-2.05.02-qt5.deb

sudo apt-get update
sudo apt-get install -f

cd ..
echo "Cleaning up"
rm -rf deconz
