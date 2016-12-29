#!/bin/sh

# Generate keys for vagrant user
mkdir -p ~/.ssh
ssh-keygen -trsa -f ~/.ssh/id_rsa -q -N ""
# sudo chown vagrant.vagrant ~/.ssh/id_rsa
# sudo chown vagrant.vagrant ~/.ssh/id_rsa.pub

# Setup passwordless access vagrant->vagrant
echo >> ~/.ssh/authorized_keys
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

# #Fix perms
# sudo chmod 700 ~/.ssh
# sudo chmod 600 ~/.ssh/id_rsa
