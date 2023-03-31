#!/bin/bash

addresses=$(ip a | awk '/inet / {print $2 " " $NF}')

declare -A dict_test

# Nested works good
echo "Nested loop result"
while IFS=$'\n' read -ra TEMP; do
    lines+=("$TEMP")
    while IFS=' ' read -ra TEMP2; do
        echo ${TEMP2[0]}
        echo ${TEMP2[1]}
        dict_test["${TEMP2[0]}"]="${TEMP2[1]}"
    done <<< "$TEMP"
done <<< "$addresses"

echo "Try to print the dict"
for val in "${!dict_test[@]}"; do
   echo "$val - ${dict_test[$val]}"
done
