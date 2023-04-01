#!/usr/bin/env bash
# TODO - Globally replace echos with real commands (echo is used for testing only)

if [[ $EUID -ne 0 ]]; then
  echo "Root privileges needed" 1>&2
  exit 1
fi

trap 'trap - SIGTERM && kill 0' SIGINT SIGTERM  # To avoid recursive SIGTERM catching

declare -A worker_result
read_stream () {
  # $1 - data stream to split
  while IFS=$'\n' read -ra TEMP; do
    while IFS=' ' read -ra TEMP2; do
        if [ -z "${TEMP2[0]}" ]; then # Trailing newline removal
          continue
        fi
        worker_result["${TEMP2[0]}"]="${TEMP2[1]}"
    done <<< "${TEMP[@]}"
done < "$1"
}

# Read the file
read_stream "$1"

# Check the mode (Open5Gs or UERANSIM). We assume there will not be any mixes
mode="Open5Gs"
for key in "${!worker_result[@]}"; do
  if [[ "$key" == "gnb" || "$key" == "ue" ]]; then
    mode="UERANSIM"
  fi
done
echo "Detected $mode mode based on the provided text file $1"

# Perform UERANSIM specific commands to start the UE and gNb simulators
if [[ "$mode" == "UERANSIM" ]]; then
  # Fetch sudo caller home dir. Note - SUDO_UID is preserved even in case normal user uses sudo -s to run commands
  SRC_USERNAME=$(id -nu "$SUDO_UID")
  SRC_PATH=$(eval echo "~$SRC_USERNAME/UERANSIM")
  # Check callee home folder, then root home folder. If in neither UERANSIM exists, exit
  echo "cd ${SRC_PATH}/UERANSIM" || echo "cd $HOME/UERANSIM" || echo "exit 1"

  for key in "${!worker_result[@]}"; do
    echo "build nr-$key -c ${worker_result[$key]} &"
  done
# Perform Open5Gs specific commands - more to do
else
  # Start daemons
  for key in "${!worker_result[@]}"; do
    if [[ -z "${worker_result[$key]}" ]]; then
      echo "/bin/open5gs-${key}d &"
    else
      echo "/bin/open5gs-${key}d -c ${worker_result[$key]} &"
    fi
  done
  # Enable NAT and port forwards for Open5Gs related inferfaces:
  echo "sudo sysctl -w net.ipv4.ip_forward=1"  # Ip forwarding
  unset worker_result; declare -A worker_result  # Reset the variable to fetch different data
  ip a | awk '/inet / && $NF!~/lo/ {print $NF " " $2}' | tee temp_file  # Fetch interfaces and their IPs, except for lo (TODO change lo to ogstun)
  read_stream "temp_file"
  for key in "${!worker_result[@]}"; do
    echo "sudo iptables -t nat -A postrouting -s ${key} ! -o ${worker_result[$key]} -j MASQUERADE"  # NAT
  done
fi

for i in "${!worker_result[@]}"; do
  echo "key: $i ; val: ${worker_result[$i]}"
done



