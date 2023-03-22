#!/bin/bash
# Script is most likely operational. Fixed issue with mongod process persisting
if [[ $EUID -ne 0 ]]; then
  echo "Root privileges needed. Installation cancelled" 1>&2
  exit 1
fi

if [[ -f "/bin/open5gs-amfd" ]]; then
  echo "Open5gs is most likely installed. One of the binaries are present in /bin. Installation cancelled" 1>&2
  exit 2
fi

# Fetching dependency for open5gs and adding repository
apt-get update
apt-get install dialog apt-utils -y  # Required to not encounter "tty required" error
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

sleep 2  # Just in case mongo takes some time to launch
# Checking if mongodb works.
if pgrep -x "mongod" > /dev/null; then
  echo "Mongo daemon is running OK!"
else
  echo "Mongo daemon is not working. Attempting to fix it..."
  mkdir -p /data/db  # or /usr/local/var/data/db - needs to be checked. Maybe dependent on mongo version
  # Alternative if the restart stops working:
  #mongod > /dev/null 2>&1 & # Run mongod in background; redirect stderr to stdout, and stdout to /dev/null
  #sleep 2
  #pkill mongod
  systemctl restart mongod
  sleep 3
  if pgrep -x "mongod" > /dev/null; then
    echo "Fix successful! Mongo daemon is running"
  else
    echo "Failed to fix mongo daemon. Aborting installation!"
    exit
  fi
fi

# Finalise open5gs installation
apt-get install open5gs -y

# Fetch cli interface for open5gs subscriber database
wget https://raw.githubusercontent.com/open5gs/open5gs/main/misc/db/open5gs-dbctl -O /usr/bin/open5gs-dbctl
chmod +x /usr/bin/open5gs-dbctl

# Change hostname and hosts file
echo "open5gs" > /etc/hostname
sed -i '2i 127.0.1.1 open5gs' /etc/hosts # 2i - insert at 2nd line

echo "Rebooting in 5 seconds..."
sleep 5
shutdown -r now
