#!/bin/bash

echo "Iniciando limpeza..."

sync
echo 3 > /proc/sys/vm/drop_caches 2>/dev/null

echo "Limpeza concluída"