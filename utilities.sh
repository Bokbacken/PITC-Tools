#!/bin/bash

sudo apt update
sudo apt install -y network-manager python3 git iproute2 python-flask
sudo apt install iperf3 wireshark
sudo usermod -a -G wireshark pi
sudo cp /home/pi/PITC-Tools/Bridge/br-start.sh /etc/init.d/brstart
sudo update-rc.d br-start.sh defaults
sudo nano /etc/init.d/brstart
sudo cp /home/pi/PITC-Tools/manipulate/manipulate.desktop /usr/share/applications/manipulate.desktop
