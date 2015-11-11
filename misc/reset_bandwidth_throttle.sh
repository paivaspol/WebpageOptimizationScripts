#!/bin/bash
sudo dnctl flush
sudo pfctl -i bridge100 -f /etc/pf.conf
