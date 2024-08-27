#!/bin/bash

# Default values
BRIDGE_NAME="br0"
IFACE1="eth1"
IFACE2="eth2"

# Check if arguments are provided
if [ $# -eq 3 ]; then
    BRIDGE_NAME=$1
    IFACE1=$2
    IFACE2=$3
elif [ $# -ne 0 ]; then
    echo "Usage: $0 [bridge_name interface1 interface2]"
    echo "Example: $0 br0 eth1 eth2"
    exit 1
fi

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

# Function to delete connections by name
delete_connections_by_name() {
    local conn_name=$1
    echo "Checking for existing connections named $conn_name..."
    local uuids=$(nmcli -t -f UUID,NAME connection show | grep "$conn_name" | cut -d: -f1)

    for uuid in $uuids; do
        echo "Deleting $conn_name with UUID $uuid..."
        nmcli connection delete uuid $uuid
    done
}

# Delete existing connections
delete_connections_by_name $BRIDGE_NAME
delete_connections_by_name "br-$IFACE1"
delete_connections_by_name "br-$IFACE2"

# Create the bridge interface if it doesn't already exist
if ! ip link show $BRIDGE_NAME &> /dev/null; then
    echo "Creating the bridge interface..."
    ip link add name $BRIDGE_NAME type bridge
else
    echo "Bridge interface $BRIDGE_NAME already exists."
fi

# Add physical interfaces to the bridge
echo "Adding $IFACE1 and $IFACE2 to the bridge..."
ip link set $IFACE1 master $BRIDGE_NAME
ip link set $IFACE2 master $BRIDGE_NAME

# Bring up the interfaces
echo "Bringing up the interfaces..."
ip link set dev $BRIDGE_NAME up
ip link set dev $IFACE1 up
ip link set dev $IFACE2 up

# Set promiscuous mode
echo "Setting promiscuous mode..."
ip link set $BRIDGE_NAME promisc on
ip link set $IFACE1 promisc on
ip link set $IFACE2 promisc on

# Flush IP addresses from physical interfaces
echo "Flushing IP addresses from $IFACE1 and $IFACE2..."
ip addr flush dev $IFACE1
ip addr flush dev $IFACE2

# Disable STP and set forward delay to 0
echo "Configuring bridge settings..."
nmcli connection add type bridge ifname $BRIDGE_NAME
nmcli connection add type ethernet slave-type bridge con-name br-$IFACE1 ifname $IFACE1 master $BRIDGE_NAME
nmcli connection add type ethernet slave-type bridge con-name br-$IFACE2 ifname $IFACE2 master $BRIDGE_NAME
nmcli connection modify $BRIDGE_NAME bridge.stp no
nmcli connection modify $BRIDGE_NAME bridge.forward-delay 0
nmcli connection modify $BRIDGE_NAME bridge.multicast-snooping no

# Adjust bridge settings to ensure proper handling of multicast and broadcast packets
echo "Adjusting bridge settings for multicast and broadcast traffic..."
ip link set $BRIDGE_NAME type bridge ageing_time 0

# Bring up the bridge connection
echo "Bringing up the bridge connection..."
nmcli connection up $BRIDGE_NAME

# Change the mask so that all traffic is forwarded, including LLDP
ip link set $BRIDGE_NAME type bridge group_fwd_mask 0x4018

# Verify the configuration
echo "Verifying the configuration..."
nmcli connection show
nmcli device status
ip addr show $BRIDGE_NAME
ip link show $BRIDGE_NAME
ip link show $IFACE1
ip link show $IFACE2

# Display bridge details
bridge link show $BRIDGE_NAME

echo "Bridge setup complete. Please check your PROFINET devices."
