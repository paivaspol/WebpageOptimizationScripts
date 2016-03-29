#!/bin/bash
./configure --enable-http-violations \
            --with-openssl \
            --disable-eui \
            --enable-linux-netfilter \
            --enable-auth \
            --enable-ssl-crtd \
            --prefix=/home/vaspol/Research/squid-no-cache \
            CPPFLAGS='-Wno-error=deprecated-declarations' \
            LDFLAGS='-lresolv'

