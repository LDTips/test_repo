#!/bin/bash
# IMPORTANT NOTE: SCRIPT NOT TESTED!
if [[ $EUID -ne 0 ]]; then
  echo "Root privileges needed"
  exit
fi
# Fetching needed things for open5gs
#echo "Fetching some dependencies for open5gs..."
apt-get install software-properties-common -y
add-apt-repository ppa:open5gs/latest -y
#echo "OK"
# Installing mongo db
#echo "Fetching dependencies for mongodb..."
apt-get install gnupg -y
# Version 4 is used because for Version 6 mongo command is not available
# Version 5 requires some CPU flags that might not be available on older CPUs
wget -qO - https://www.mongodb.org/static/pgp/server-4.0.asc | sudo apt-key add -
echo "deb [ arch=amd64] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.0.list
apt-get update
#echo "OK"

#echo "Installing mongodb..."
apt-get install -y mongodb-org
#echo "OK"

# Checking if mongodb works
#echo "Checking if mongo daemon works..."
if pgrep -x "mongod" > /dev/null; then
  #echo "Mongo daemon is running OK!"
  true # placeholder
else
  #echo "Not working. Attempting to fix mongo daemon..."
  mkdir -p /usr/local/var/data/db
  mongod
  systemctl restart mongod
  if pgrep -x "mongod" > /dev/null; then
    #echo "Fix successful! Mongo daemon is running"
    true # placeholder
  else
    #echo "Failed to fix mongo daemon. Aborting installation!"
    exit
  fi
fi

apt-get install open5gs

# Fetch cli interface for the database
#echo "Fetching open5gs database command line tool from github..."
wget https://raw.githubusercontent.com/open5gs/open5gs/main/misc/db/open5gs-dbctl -O /usr/bin/open5gs-dbctl
chmod +x /usr/bin/open5gs-dbctl
#echo "OK"

# Change hostname and hosts file
#echo "Changing hostname and hosts files..."
echo "open5gs" > /etc/hostname
sed -i '2i 127.0.1.1 open5gs' /etc/hosts # 2i - insert at 2nd line
#echo "OK"

echo "Rebooting in 5 seconds..."
sleep 5
shutdown -r now
