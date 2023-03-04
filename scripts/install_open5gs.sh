#!/bin/bash
# IMPORTANT NOTE: SCRIPT NOT TESTED!
if [[ $EUID -ne 0 ]]; then
  echo "Root privileges needed"
  exit
fi
# Fetching needed things for open5gs
# Fetching some dependencies for open5gs
apt-get install software-properties-common -y
add-apt-repository ppa:open5gs/latest -y

# Installing mongo db
# Version 4 is used because for Version 6 mongo command is not available
# Version 5 requires some CPU flags that might not be available on older CPUs
apt-get install gnupg -y
wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
apt-get update
apt-get install -y mongodb-org

sleep 3
# Checking if mongodb works
if pgrep -x "mongod" > /dev/null; then
  echo "Mongo daemon is running OK!"
else
  echo "Not working. Attempting to fix mongo daemon..."
  mkdir -p /data/db  # or /usr/local/var/data/db - needs to be checked. Maybe dependent on mongo version
  mongod
  systemctl restart mongod
  if pgrep -x "mongod" > /dev/null; then
    echo "Fix successful! Mongo daemon is running"
  else
    echo "Failed to fix mongo daemon. Aborting installation!"
    exit
  fi
fi

# Finalise open5gs installation
apt-get install open5gs

# Fetch cli interface for open5gs subscriber database
wget https://raw.githubusercontent.com/open5gs/open5gs/main/misc/db/open5gs-dbctl -O /usr/bin/open5gs-dbctl
chmod +x /usr/bin/open5gs-dbctl

# Change hostname and hosts file
echo "open5gs" > /etc/hostname
sed -i '2i 127.0.1.1 open5gs' /etc/hosts # 2i - insert at 2nd line

echo "Rebooting in 5 seconds..."
sleep 5
shutdown -r now
