#!/bin/bash

BUILD_DIRECTORY="/home/ubuntu/build"

cd ~

# Make sure that we are at the home directory.
mkdir ~

# Requirements for running this script: git
sudo apt-get -y install git python

sudo pip install Flask

# Create the default build directory.
mkdir $BUILD_DIRECTORY

#######################################################
#  nghttp2
#######################################################

# install necessary dependencies for nghttp2.
sudo apt-get -y install g++ make binutils autoconf automake autotools-dev libtool pkg-config \
  zlib1g-dev libcunit1-dev libssl-dev libxml2-dev libev-dev libevent-dev libjansson-dev \
  libjemalloc-dev cython python3-dev python-setuptools
if [ $? -eq 0 ]
then
    echo "Installed nghttp2 dependencies"
else
    echo "nghttp2 installation failed."
    exit 1
fi

# clone the repository.
if [ ! -d ~/nghttp2 ]; then
    git clone https://github.com/nghttp2/nghttp2.git
fi
cd nghttp2

# build nghttp2
autoreconf -i
automake
autoconf
./configure --prefix=$BUILD_DIRECTORY --enable-app
make
export PYTHONPATH=/home/ubuntu/build/lib/python2.7/site-packages/
make install
if [ $? -eq 0 ]
then
    echo "nghttp2 was built and installed."
else
    echo "nghttp2 built failed"
    exit 1
fi

cd ~

#######################################################
#  squid
#######################################################

# Download and build squid.
wget http://apple-pi.eecs.umich.edu/squid-src.tar.gz
tar xvzf squid-src.tar.gz
rm squid-src.tar.gz
cd squid-src
./configure_script.sh $BUILD_DIRECTORY
make
make install
if [ $? -eq 0 ]
then
    echo "squid was built and installed."
else
    echo "squid built failed"
    exit 1
fi

# Setup the config file and SSL database.
cp squid.conf $BUILD_DIRECTORY/etc
if [ $? -eq 0 ]
then
    echo "squid config file was copied."
else
    echo "squid config file copy error."
    exit 1
fi

mkdir $BUILD_DIRECTORY/var/lib
$BUILD_DIRECTORY/libexec/ssl_crtd -c -s $BUILD_DIRECTORY/var/lib/ssl_db
$BUILD_DIRECTORY/sbin/squid -z

cd ~

#####################################################
 apache
#####################################################

First get httpd
do apt-get -y install libpcre3 libpcre3-dev libapr1-dev libaprutil1-dev

et http://apache.mirrors.tds.net//httpd/httpd-2.4.20.tar.gz
r xvzf httpd-2.4.20.tar.gz
 httpd-2.4.20.tar.gz

wget http://www.carfab.com/apachesoftware//apr/apr-1.5.2.tar.gz
tar xvzf apr-1.5.2.tar.gz
rm apr-1.5.2.tar.gz
mv apr-1.5.2 httpd-2.4.20/srclib/apr

wget http://www.carfab.com/apachesoftware//apr/apr-util-1.5.4.tar.gz
tar xvzf apr-util-1.5.4.tar.gz
rm apr-util-1.5.4.tar.gz
mv apr-util-1.5.4 httpd-2.4.20/srclib/apr-util

cd httpd-2.4.20
./configure --prefix=$BUILD_DIRECTORY --enable-mpms-shared=all
if [ $? -eq 0 ]
then
    echo "httpd configured."
else
    echo "httpd configuration failed"
    exit 1
fi

make
make install
if [ $? -eq 0 ]
then
    echo "httpd was built and installed."
else
    echo "httpd built failed"
    exit 1
fi

cd ~

#######################################################
#  Mahimahi
#######################################################

# Install Mahimahi dependencies
sudo apt-get -y install protobuf-compiler libprotobuf-dev autotools-dev \
autotools-dev dh-autoreconf iptables pkg-config dnsmasq-base debhelper \
libssl-dev ssl-cert libxcb-present-dev libcairo2-dev libpango1.0-dev

git clone https://github.com/paivaspol/mahimahi.git
cd mahimahi
./autogen.sh
./configure --prefix=$BUILD_DIRECTORY
make
sudo make install
if [ $? -eq 0 ]
then
    echo "Mahimahi was built and installed."
else
    echo "Mahimahi built failed"
    exit 1
fi

cd ~

