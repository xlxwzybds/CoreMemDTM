#!/bin/bash

cfg_file="../config/gainestown_3D_16core16bank.cfg"

update_latency_and_run() {
    local latency_value=$1

    sed -i "s/^\([[:space:]]*latency[[:space:]]*=[[:space:]]*\)[0-9]\+/latency = $latency_value/" "$cfg_file"

    if grep -q "latency = $latency_value" "$cfg_file"; then
        echo "Latency parameter updated to $latency_value successfully."
    else
        echo "Failed to update latency parameter to $latency_value."
        exit 1
    fi

    python3 run.py
}

update_dynamic_power_and_run() {
    local Dynamic_power_value=$1

    sed -i "s/^\([[:space:]]*latency[[:space:]]*=[[:space:]]*\)[0-9]\+/latency = $latency_value/" "$cfg_file"

    if grep -q "latency = $latency_value" "$cfg_file"; then
        echo "Latency parameter updated to $latency_value successfully."
    else
        echo "Failed to update latency parameter to $latency_value."
        exit 1
    fi

    python3 run.py
}

latency_values=(15  75  135 165 )

for latency in "${latency_values[@]}"
do
    update_latency_and_run $latency
done
