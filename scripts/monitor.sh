#!/usr/bin/env bash
# Memory monitor for training runs on the DGX Spark.
#
#   ./scripts/monitor.sh logs/main-mem.log &
#
# Unified memory means one runaway allocation can wedge the whole box rather than
# raising a clean OOM, so during any long run this writes a timestamped line every
# 30 seconds. If free memory collapses, kill the training job before the machine
# swaps itself to death.

set -euo pipefail

OUT="${1:-logs/mem.log}"
mkdir -p "$(dirname "$OUT")"

echo "monitoring to $OUT every 30s (ctrl-c to stop)"
while true; do
    {
        printf '%s ' "$(date '+%Y-%m-%d %H:%M:%S')"
        # Unified memory: system view.
        free -g | awk '/^Mem:/ {printf "mem_used=%sG mem_free=%sG avail=%sG ", $3, $4, $7}'
        # GPU view of the same pool, when the query is supported.
        nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null \
            | awk -F', ' '{printf "gpu_used=%sMiB gpu_total=%sMiB", $1, $2}'
        printf '\n'
    } >> "$OUT"
    sleep 30
done
