#!/bin/bash
# Tested once. Works. Requires some more extensive testing
# This script is less complex than open5gs
if [[ $EUID -ne 0 ]]; then
  echo "Root privileges needed"
  exit
fi
# TODO - Implement an if statement that aborts installation if UERANSIM is installed

# Fetch dependencies
apt-get update
apt-get install build-essential libsctp-dev lksctp-tools iproute2 g++ gcc -y
snap install cmake --classic

# Fetch UERANSIM files
cd ~ || exit
git clone https://github.com/aligungr/UERANSIM

# Build UERANSIM. Note: takes some time. Recommended to make some coffee or tea in the meantime
cd ~/UERANSIM || exit
make

# Change hostname and hosts file
echo "UERANSIM" > /etc/hostname
sed -i '2i 127.0.1.1 UERANSIM' /etc/hosts # 2i - insert at 2nd line

echo "Rebooting in 5 seconds..."
sleep 5
shutdown -r now
