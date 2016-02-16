#!/bin/bash

# Reset dummynet to default config
dnctl -f flush

# Compose an addendum to the default config; creates a new anchor
# and a table whose contents are loaded from the specified file
read -d '' -r PF <<EOF
dummynet-anchor "4G"
anchor "4G"
EOF

# Reset PF to default config and apply our addendum
(cat /etc/pf.conf && echo "$PF") | pfctl -q -f -

# Configure the new anchor
cat <<EOF | pfctl -q -a 4G -f -
dummynet out proto tcp from any to 192.168.2.0/24 port 1:65535 pipe 1
dummynet in proto tcp from 192.168.2.0/24 to any port 1:65535 pipe 2
pass out quick on bridge100 inet proto tcp from any to any port 1:65535
pass in quick on bridge100 inet proto tcp from any to any port 1:65535
EOF

# Dummynet

# Create the dummynet queue
dnctl pipe 1 config bw 6Mbit/s delay 100ms
dnctl pipe 2 config bw 2Mbit/s

# Activate PF
pfctl -E
