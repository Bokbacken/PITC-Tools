#!/bin/bash

sudo apt update
sudo apt install iperf3 wireshark
sudo usermod -a -G wireshark pi
sudo cp /home/pi/PITC-Tools/bridge/br-start.sh /etc/init.d/brstart
sudo update-rc.d brstart defaults
sudo nano /etc/init.d/brstart
sudo cp /home/pi/PITC-Tools/manipulate/manipulate.desktop /usr/share/applications/manipulate.desktop
