# PITC-Tools
Various Tools for PITC trainings

Transparent bridging of two ethernet interfaces, forwarding all packages including LLDP for PROFINET.

Usage:

sudo ./br-start.sh br0 eth1 eth2

Possibility to use wireshark on br0 to see all traffic passing through this transparent bridge, switches and devices connected to this bridge will only see it as a ethernet cable.

To add IP address to the br0 interface use:
sudo ip addr add 172.16.0.210/24 dev br0

in br-start.sh the last row can be changed to set an ip address when the bridge is started.

To automatically start this script copy it to /etc/init.d
then run
sudo update-rc.d br-start.sh defaults

reboot the raspberry pi and make sure the bridge is starting.
