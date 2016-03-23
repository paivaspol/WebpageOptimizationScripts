# Mahimahi _delayshell_ works by setting up a new p2p network within the machine.
# Everything running inside the shell will not be accessible by the outside word.
# Thus, we need to perform NAT on the incoming traffic so that the traffic will be 
# sent to the _delayshell_ properly.
# 
# This can be done with two tools included in a linux distribution.
#   * route
#   * iptables
#
# _delayshell_ uses _packetshell_ and it creates an uplink route, from the 
# p2p network, for us already: p2p IP address to 0.0.0.0/32. We need to manually
# create a downlink route, which is from 0.0.0.0/32 to p2p IP address.
#
# Once we create the downlink route, we then need to perform proper NAT on the
# traffic.

# Usage
#   ./setup-nat-for-forwarding-traffic.sh [p2p IP address] [src port] [dst port (within p2p network)] [interface]
# Example:
#   ./setup-nat-for-forwarding-traffic.sh 100.64.0.2 80 80 delay-1241
# 
# These information can be retrieved from `ifconfig`.

# Setup the downlink route.
gateway=$1
sport=$2
dport=$3
interface=$4
sudo route add -net 0.0.0.0 netmask 255.255.255.255 gw $gateway

# Setup forwarding in iptables
sudo iptables -I FORWARD -d $gateway -p tcp --dport $dport -j ACCEPT
sudo iptables -I FORWARD -d $gateway -p tcp --sport $sport -j ACCEPT

# Setup prerouting and postrouting to the p2p network.
sudo iptables -t nat -I PREROUTING -p tcp --dport $sport -j DNAT --to-destination $gateway:$dport
sudo iptables -t nat -I POSTROUTING -d $gateway -o $interface -j MASQUERADE
