#!/bin/bash

echo "Status do sistema:"
echo ""

echo "CPU:"
cpu1=($(grep '^cpu ' /proc/stat))
idle1=${cpu1[4]}
total1=0

for value in "${cpu1[@]:1}"; do
    total1=$((total1 + value))
done

sleep 1

cpu2=($(grep '^cpu ' /proc/stat))
idle2=${cpu2[4]}
total2=0

for value in "${cpu2[@]:1}"; do
    total2=$((total2 + value))
done

diff_idle=$((idle2 - idle1))
diff_total=$((total2 - total1))

if [ "$diff_total" -gt 0 ]; then
    cpu_usage=$(( (100 * (diff_total - diff_idle)) / diff_total ))
    echo "${cpu_usage}% usado"
else
    echo "indisponível"
fi

echo ""
echo "Memória:"
mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
mem_available=$(grep MemAvailable /proc/meminfo | awk '{print $2}')

if [ -n "$mem_total" ] && [ -n "$mem_available" ] && [ "$mem_total" -gt 0 ]; then
    mem_used=$((mem_total - mem_available))
    mem_used_mb=$((mem_used / 1024))
    mem_total_mb=$((mem_total / 1024))
    mem_percent=$(( (100 * mem_used) / mem_total ))

    echo "${mem_percent}% usado"
    echo "${mem_used_mb}MB / ${mem_total_mb}MB"
else
    echo "indisponível"
fi

echo ""
echo "Disco:"
df -h / | awk 'NR==2 {print $5 " usado"}'