#!/bin/bash

# Check for root privileges
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

# Install NetworkManager if not already installed
if ! command -v nmcli &> /dev/null; then
    echo "NetworkManager not found. Installing..."
    apt-get update
    apt-get install -y network-manager
else
    echo "NetworkManager is already installed."
fi

# Create the bridge interface if it doesn't already exist
if ! ip link show br0 &> /dev/null; then
    echo "Creating the bridge interface..."
    ip link add name br0 type bridge
else
    echo "Bridge interface br0 already exists."
fi

# Add physical interfaces to the bridge
echo "Adding eth1 and eth2 to the bridge..."
ip link set eth1 master br0
ip link set eth2 master br0

# Bring up the interfaces
echo "Bringing up the interfaces..."
ip link set dev br0 up
ip link set dev eth1 up
ip link set dev eth2 up

# Set promiscuous mode
echo "Setting promiscuous mode..."
ip link set br0 promisc on
ip link set eth1 promisc on
ip link set eth2 promisc on

# Flush IP addresses from physical interfaces
echo "Flushing IP addresses from eth1 and eth2..."
ip addr flush dev eth1
ip addr flush dev eth2

# Disable STP and set forward delay to 0
echo "Configuring bridge settings..."
nmcli connection add type bridge ifname br0
nmcli connection add type ethernet slave-type bridge con-name br-eth1 ifname eth1 master br0
nmcli connection add type ethernet slave-type bridge con-name br-eth2 ifname eth2 master br0
nmcli connection modify br0 bridge.stp no
nmcli connection modify br0 bridge.forward-delay 0
nmcli connection modify br0 bridge.multicast-snooping no

# Adjust bridge settings to ensure proper handling of multicast and broadcast packets
echo "Adjusting bridge settings for multicast and broadcast traffic..."
ip link set br0 type bridge ageing_time 0

# Bring up the bridge connection
echo "Bringing up the bridge connection..."
nmcli connection up br0

# Change the mask so that all traffic is forwarded, including LLDP
ip link set br0 type bridge group_fwd_mask 0x4018

# Verify the configuration
echo "Verifying the configuration..."
nmcli connection show
nmcli device status
ip addr show br0
ip link show br0
ip link show eth1
ip link show eth2

# Display bridge details
bridge link show br0

echo "Bridge setup complete. Please check your PROFINET devices."
