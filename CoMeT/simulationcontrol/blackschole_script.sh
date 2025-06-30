#!/bin/bash

cfg_file="../config/gainestown_3D_16core16bank.cfg"

update_latency_and_run() {
    local latency_value=$1
    local dynamic_power_value=$2
    local leakage_power_value=$3

    sed -i "s/^\([[:space:]]*latency_lowpower[[:space:]]*=[[:space:]]*\)[0-9]*\.*[0-9]*/\1$latency_value/" "$cfg_file"
    sed -i "s/^\([[:space:]]*lpm_dynamic_power[[:space:]]*=[[:space:]]*\)[0-9]*\.*[0-9]*/\1$dynamic_power_value/" "$cfg_file"
    sed -i "s/^\([[:space:]]*lpm_leakage_power[[:space:]]*=[[:space:]]*\)[0-9]*\.*[0-9]*/\1$leakage_power_value/" "$cfg_file"

    # 检查是否成功更新
    if grep -q "latency_lowpower = $latency_value" "$cfg_file" &&
       grep -q "lpm_dynamic_power = $dynamic_power_value" "$cfg_file" &&
       grep -q "lpm_leakage_power = $leakage_power_value" "$cfg_file"; then
        echo "Parameters updated successfully:"
        echo "  latency_lowpower = $latency_value"
        echo "  lpm_dynamic_power = $dynamic_power_value"
        echo "  lpm_leakage_power = $leakage_power_value"
    else
        echo "Failed to update parameters."
        exit 1
    fi

    # 运行 Python 脚本
    python3 run.py
}

# 定义参数数组
latency_values=(165 195)
dynamic_power_values=(0.6 0.5)
leakage_power_values=(0.5 0.45)

# 循环更新并运行
for i in "${!latency_values[@]}"; do
    latency=${latency_values[$i]}
    dynamic_power=${dynamic_power_values[$i]}
    leakage_power=${leakage_power_values[$i]}
    echo "Running with latency=$latency, dynamic_power=$dynamic_power, leakage_power=$leakage_power"
    update_latency_and_run "$latency" "$dynamic_power" "$leakage_power"
done
