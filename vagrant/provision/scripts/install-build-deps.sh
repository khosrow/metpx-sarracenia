#!/bin/sh

# Install packages needed for building
sudo apt-get update -q
sudo apt-get install -y unzip
sudo apt-get install -y devscripts
sudo apt-get install -y dpkg-dev
sudo apt-get install -y debhelper
sudo apt-get install -y python3-setuptools
sudo apt-get install -y python-docutils
sudo apt-get install -y git
sudo apt-get install -y python3-pkg-resources
sudo apt-get install -y ksh
