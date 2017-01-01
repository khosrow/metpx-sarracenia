#!/bin/sh

# Install packages needed for building
sudo apt-get update -q
sudo apt-get install -y unzip
sudo apt-get install -y devscripts
sudo apt-get install -y dpkg-dev
sudo apt-get install -y debhelper
sudo apt-get install -y python-docutils
