# PITC-Tools
Various Tools for PITC trainings

Transparent bridging of two ethernet interfaces, forwarding all packages including LLDP for PROFINET
usage:
sudo ./startbridge.sh br0 eth1 eth2
Possibility to use wireshark on br0 to see all traffic passing through this transparent bridge, switches and devices connected to this bridge will only see it as a ethernet cable.

