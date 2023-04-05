#!/usr/bin/env bash

# This script is not idiot proof. It's assumed the inputs are correct since they are mostly generated from Python
# "Make something idiot proof, they'll make a better idiot" ~Unknown
# TODO - Globally replace echos with real commands (echo is used for testing only)
if [[ $EUID -ne 0 ]]; then
  echo "Root privileges needed" 1>&2
  exit 1
fi

trap 'trap - SIGTERM && kill 0' SIGINT SIGTERM  # To avoid recursive SIGTERM catching

declare -A worker_result
read_stream () {
  # $1 - data stream to split
  while read -r key val || [[ -n "$key" ]]; do
    if [[ -z "$val" ]]; then
      val="default"
    fi
    if [[ -n ${worker_result[${key}]} ]]; then
      worker_result["$key"]+=":${val}"
    else
      worker_result["$key"]="${val}"
    fi
  done < "$1"
}

# Read the file
read_stream "$1"

# Check the mode (Open5Gs or UERANSIM). We assume there will not be any mixes
mode="Open5Gs"
for key in "${!worker_result[@]}"; do
  if [[ "$key" == "gnb" || "$key" == "ue" ]]; then
    mode="UERANSIM"
    break
  fi
done
echo "Detected $mode mode based on the provided text file $1"

# Perform UERANSIM specific commands to start the UE and gNb simulators
if [[ "$mode" == "UERANSIM" ]]; then
  # Fetch sudo caller home dir. Note - SUDO_UID is preserved even in case normal user uses sudo -s to run commands
  SRC_USERNAME=$(id -nu "${SUDO_UID}")
  SRC_PATH=$(getent passwd "${SRC_USERNAME}" | cut -d":" -f6)
  # Check callee home folder, then root home folder. If in neither UERANSIM exists, exit
  echo "cd ${SRC_PATH}/UERANSIM" || echo "cd ${HOME}/UERANSIM" || echo "exit 1"

  for key in "${!worker_result[@]}"; do
    echo "build nr-${key} -c ${worker_result[${key}]} &"
  done
# Perform Open5Gs specific commands - more to do than in the UERANSIM case
else
  # Check the availability of yq. Install it if not found. We need it only for Open5Gs UPF
  if ! yq &> /dev/null && [[ -v ${worker_result["upf"]} ]]; then
    apt-get update
    apt-get install yq -y
  fi

  # Start daemons
  for key in "${!worker_result[@]}"; do
    IFS=":" read -ra split <<< "${worker_result[${key}]}"
    for path in "${split[@]}"; do
      if [[ "$path" == "default" ]]; then
        echo "/bin/open5gs-${key} &"
      else
        echo "/bin/open5gs-${key} -c ${path} &"
      fi
    done
  done
  sleep 5  # Give some time for daemons and interfaces to start

  # Enable NAT and port forwards for Open5Gs related interfaces:
  echo "sudo sysctl -w net.ipv4.ip_forward=1"
  if [[ "${worker_result["upf"]}" == "default" ]]; then
    # Point to default config if it wasn't specified for the purpose getting the path in yq
    worker_result["upf"]="/etc/open5gs/upf.yaml"
  fi
  # Read from upf.subnet array fields that have addr and dev field. Print in format "addr dev" to a file
  # This is required for NAT rules for Open5Gs tunnel interfaces. dev is the interface name for an address addr
  # File is required because of how read_stream is implemented
  yq '.upf.subnet[] | select(has("addr") and has("dev")) | .addr + " " + .dev' < "${worker_result["upf"]}" > temp_file
  unset worker_result; declare -A worker_result  # From this point worker_result will be interface, not daemon info
  read_stream "temp_file"
  rm -f "temp_file"
  for key in "${!worker_result[@]}"; do
    echo "ip tuntap add name ${key} mode tun" 2> /dev/null # If interface exists err will be printed, but that's not an issue
    echo "ip addr add ${worker_result[${key}]} dev ${key}"
    echo "ip link set ${key} up"
    echo "sudo iptables -t nat -A POSTROUTING -s ${key} ! -o ${worker_result[${key}]} -j MASQUERADE"  # NAT
  done
fi
