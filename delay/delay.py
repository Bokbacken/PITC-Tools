from scapy.all import *
from netfilterqueue import NetfilterQueue
import time

# Function to add delay to packets
def delay_packet(packet):
    # Create Scapy packet from raw payload
    scapy_packet = IP(packet.get_payload())
    
    # Introduce a 100ms delay
    time.sleep(0.1)
    
    # Accept and forward the packet
    packet.accept()

# Initialize NetfilterQueue and bind to queue number 1
nfqueue = NetfilterQueue()
nfqueue.bind(1, delay_packet)

try:
    print("Starting packet processing with 100ms delay...")
    nfqueue.run()  # Start processing packets
except KeyboardInterrupt:
    print("\nStopping packet processing...")

# Clean up
nfqueue.unbind()

# Flush the iptables rule
os.system("sudo iptables -D FORWARD -i br0 -j NFQUEUE --queue-num 1")
