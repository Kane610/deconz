#!/bin/bash

echo "Deconz installer"

cd /tmp/
if [ -d "deconz" ]; then
    echo "Removing old Deconz installation"
    sudo rm -rf deconz
fi
mkdir deconz
cd deconz/

wget http://www.dresden-elektronik.de/rpi/deconz/beta/deconz-2.04.99-qt5.deb
sudo dpkg --install deconz-2.04.99-qt5.deb

wget http://www.dresden-elektronik.de/rpi/deconz-dev/deconz-dev-2.04.99.deb
sudo apt-get install --fix-broken --assume-yes
sudo dpkg --install deconz-dev-2.04.99.deb

git clone https://github.com/dresden-elektronik/deconz-rest-plugin.git
cd deconz-rest-plugin
git checkout -b mybranch V2_04_99
qmake
make -j3
cd ..
sudo cp libde_rest_plugin.so /usr/share/deCONZ/plugins

cd ..
echo "Cleaning up"
rm -rf deconz
