#!/usr/bin/env bash
# Step 0: read-only diagnosis of the DGX Spark, run over SSH from the Mac.
#
#   ./scripts/spark_diagnose.sh buildlocalai@192.168.0.180
#
# Answers, against reality rather than spec sheets: how much unified memory is
# actually free, what's already running and holding it, whether swap is on (it
# must be off for training), how much disk is free, and whether the container
# runtime sees the GPU. Nothing here mutates anything.

set -euo pipefail

HOST="${1:?usage: spark_diagnose.sh user@host}"

ssh -o ConnectTimeout=10 "$HOST" 'bash -s' <<'REMOTE'
section() { printf '\n=== %s ===\n' "$1"; }

section "identity"
echo "host: $(hostname)   user: $(whoami)"

section "os / kernel"
grep -E "^(NAME|VERSION)=" /etc/os-release 2>/dev/null
cat /etc/dgx-release 2>/dev/null | head -6 || echo "(no /etc/dgx-release)"
uname -mr

section "gpu / driver"
nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used --format=csv 2>/dev/null \
    || nvidia-smi 2>&1 | head -12

section "unified memory"
free -h

section "swap (must be OFF during training)"
swapon --show 2>/dev/null || echo "swap: off"

section "disk"
df -h / /home 2>/dev/null | awk 'NR==1 || /\/$|\/home/'

section "top memory consumers"
ps axo rss,comm --sort=-rss 2>/dev/null | head -8 || ps aux | sort -rk 4 | head -8

section "docker"
docker --version 2>/dev/null || echo "docker: NOT FOUND"
echo "-- running containers --"
docker ps --format '{{.Names}}  {{.Image}}  {{.Status}}' 2>/dev/null || echo "(cannot query; user may need docker group)"
echo "-- local images --"
docker images --format '{{.Repository}}:{{.Tag}}  {{.Size}}' 2>/dev/null | head -10

section "ollama"
if command -v ollama >/dev/null 2>&1; then
    ollama --version 2>/dev/null | head -1
    echo "-- models resident in memory --"
    ollama ps 2>/dev/null || true
    echo "-- models on disk --"
    ollama list 2>/dev/null | head -8 || true
else
    echo "ollama: not installed"
fi

section "python / tooling"
python3 --version 2>/dev/null
command -v uv >/dev/null 2>&1 && uv --version || echo "uv: not installed"
command -v git >/dev/null 2>&1 && git --version || echo "git: NOT FOUND"
command -v tmux >/dev/null 2>&1 && echo "tmux: present" || echo "tmux: not installed"
REMOTE
