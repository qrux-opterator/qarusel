#!/bin/bash

cd /root/ceremonyclient/node ; ./qclient-2.0.4.1-linux-amd64 token coins metadata --public-rpc --config /root/ceremonyclient/node/.config | \
awk '{print $6, $0}' | sort | cut -d' ' -f2- | tail -n 10 >> /root/ringloot.txt
echo "" >> /root/ringloot.txt

mv /root/ceremonyclient/node/.config/config.yml /root/ceremonyclient/node/.config/"config$(cat /root/active_nr | tr -d '\n')"
mv /root/ceremonyclient/node/.config/keys.yml /root/ceremonyclient/node/.config/"keys$(cat /root/active_nr | tr -d '\n')"
echo "config nr: $(cat /root/active_nr) stopped, and idle"

# Read the current number and increment it by 1
current_number=$(cat /root/active_nr | tr -d '\n')
next_number=$((current_number + 1))

# If the incremented number is greater than 12, reset to 0
if [ "$next_number" -gt 12 ]; then
    echo 0 > /root/active_nr
else
    echo "$next_number" > /root/active_nr
fi

nr=$(cat /root/active_nr | tr -d '\n')
echo "[DEBUG] Current active number: $nr"

# Dynamically move config file and show exactly what happened
config_src="/root/ceremonyclient/node/.config/config$nr"
config_dest="/root/ceremonyclient/node/.config/config.yml"

if [ -f "$config_src" ]; then
    echo "[DEBUG] Moving $config_src → $config_dest"
    mv "$config_src" "$config_dest"
    if [ $? -eq 0 ]; then
        echo "[DEBUG] Successfully moved $config_src to $config_dest"
    else
        echo "[ERROR] Failed to move $config_src to $config_dest"
    fi
else
    echo "[DEBUG] Source config file $config_src does not exist."
fi

# Dynamically move keys file and show exactly what happened
keys_src="/root/ceremonyclient/node/.config/keys$nr"
keys_dest="/root/ceremonyclient/node/.config/keys.yml"

if [ -f "$keys_src" ]; then
    echo "[DEBUG] Moving $keys_src → $keys_dest"
    mv "$keys_src" "$keys_dest"
    if [ $? -eq 0 ]; then
        echo "[DEBUG] Successfully moved $keys_src to $keys_dest"
    else
        echo "[ERROR] Failed to move $keys_src to $keys_dest"
    fi
else
    echo "[DEBUG] Source keys file $keys_src does not exist."
fi
sleep 4
systemctl daemon-reload && service para restart
echo "Next Config has been started!"
