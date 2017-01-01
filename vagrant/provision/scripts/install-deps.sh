#!/bin/sh

# get all the dependencies for rabbitmq-server and metpx-sarracenia
sudo add-apt-repository ppa:ssc-hpc-chp-spc/metpx -y
sudo apt-get update -q
sudo apt-get install -y python3-setuptools
sudo apt-get install -y rabbitmq-server
sudo apt-get install -y git
sudo apt-get install -y erlang-nox
sudo apt-get install -y python3-pkg-resources
#sudo apt-get install -y apache2
#sudo apt-get install -y vsftpd
sudo apt-get install -y ksh

if [ $1 = "trusty" ]; then
	# sudo apt-get install -y python3-metpx-sarracenia
	sudo apt-get install -y python3-pip
	sudo apt-get install -y python3-amqplib
	sudo apt-get install -y python3-appdirs
	sudo apt-get install -y python3-watchdog
	sudo apt-get install -y python3-netifaces
	sudo apt-get install -y python3-humanize
	sudo apt-get install -y python3-psutil
	sudo apt-get install -y python3-paramiko
fi

if [ $1 = "precise" ]; then
	sudo apt-get install python3-dev
	sudo apt-get install python3-setuptools

	# install packages that aren't available natively
	sudo easy_install3 pip
	sudo pip3 install pyinotify
	sudo pip3 install psutil
	sudo pip3 install paramiko
	sudo pip3 install metpx-sarracenia
	sudo pip3 install --upgrade metpx-sarracenia
fi
