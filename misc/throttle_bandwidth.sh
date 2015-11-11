#!/bin/bash
sudo dnctl -f flush # Flush everything

(cat /etc/pf.conf && echo "dummynet-anchor \"4G\"" && echo "anchor \"4G\"") | sudo pfctl -f -

cat <<EOF | sudo pfctl -q -a 4G -f -
no dummynet quick on bridge100 all
dummynet in proto tcp from any to any pipe 1
dummynet out proto tcp from any to any pipe 2
EOF

sudo dnctl pipe 1 config bw 10Mbit/s
sudo dnctl pipe 2 config bw 10Mbit/s

sudo pfctl -q -e
