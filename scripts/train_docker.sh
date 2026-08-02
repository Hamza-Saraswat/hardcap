#!/usr/bin/env bash
# Run a training preset inside the Unsloth DGX Spark container, with logging.
#
#   ./scripts/train_docker.sh smoke --limit 200 --max-steps 40
#   ./scripts/train_docker.sh main
#   ./scripts/train_docker.sh main --resume
#
# HF_HOME points at the shared model cache, so the 55GB Qwen download is reused
# rather than re-fetched inside the container. Always run inside tmux for long
# runs -- the log tee means progress survives a dropped SSH session either way.

set -euo pipefail

PRESET="${1:?usage: train_docker.sh <preset> [train_lora.py args...]}"
shift || true

REPO="$(cd "$(dirname "$0")/.." && pwd)"
MODELS_DIR="${MODELS_DIR:-$HOME/hardcap-work/models}"
IMAGE="${TRAIN_IMAGE:-hardcap-train:latest}"
LOG="$REPO/logs/train-$PRESET-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$REPO/logs" "$REPO/outputs"

# -- preflight: refuse to start into a memory trap -----------------------------------------
# Unified memory means training shares one 121GB pool with everything else, and exhausting
# it doesn't fail cleanly -- it took the whole machine down once. Two checks, both hard
# refusals rather than warnings:
#   1. No other containers may be running (an orphaned model server holds tens of GB).
#   2. MemAvailable must cover the run: ~60GB for 4-bit presets, ~95GB for BF16.
RUNNING="$(docker ps --format '{{.Names}}' | grep -v "^$" || true)"
if [ -n "$RUNNING" ]; then
    echo "REFUSING TO START: containers already running:" >&2
    echo "$RUNNING" | sed 's/^/    /' >&2
    echo "Stop them first (docker stop <name>), then rerun." >&2
    exit 1
fi

NEED_GB=95
case "$PRESET" in smoke|prototype|ceiling) NEED_GB=60;; esac
AVAIL_GB="$(awk '/MemAvailable/ {printf "%d", $2/1048576}' /proc/meminfo)"
if [ "$AVAIL_GB" -lt "$NEED_GB" ]; then
    echo "REFUSING TO START: ${AVAIL_GB}GB available, preset '$PRESET' needs ~${NEED_GB}GB." >&2
    echo "Something is holding memory -- check 'docker ps' and 'free -g'." >&2
    exit 1
fi
echo "preflight ok: no containers running, ${AVAIL_GB}GB available (need ${NEED_GB}GB)"

echo "logging to $LOG"
# --entrypoint python matters: the image's default entrypoint ignores the command and
# boots a supervisord stack (Jupyter, sshd, Ollama) that idles forever. Discovered the
# hard way -- a "training run" that was actually a Jupyter server for 90 minutes.
# --memory hard-caps the container: blowing through it OOM-kills the training process,
# not the machine. This is the docker equivalent of the cgroup cap -- a host-level
# user.slice cap would not constrain containers at all.
docker run --rm --gpus all \
    --entrypoint python \
    --memory=105g --memory-swap=105g \
    -v "$REPO":/workspace -w /workspace \
    -v "$MODELS_DIR":/models -e HF_HOME=/models \
    --shm-size=16g \
    "$IMAGE" \
    training/train_lora.py --preset "$PRESET" "$@" 2>&1 | tee "$LOG"
