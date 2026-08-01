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
LOG="$REPO/logs/train-$PRESET-$(date +%Y%m%d-%H%M%S).log"
mkdir -p "$REPO/logs" "$REPO/outputs"

echo "logging to $LOG"
# --entrypoint python matters: the image's default entrypoint ignores the command and
# boots a supervisord stack (Jupyter, sshd, Ollama) that idles forever. Discovered the
# hard way -- a "training run" that was actually a Jupyter server for 90 minutes.
docker run --rm --gpus all \
    --entrypoint python \
    -v "$REPO":/workspace -w /workspace \
    -v "$MODELS_DIR":/models -e HF_HOME=/models \
    --shm-size=16g \
    unsloth/unsloth:dgxspark-latest \
    training/train_lora.py --preset "$PRESET" "$@" 2>&1 | tee "$LOG"
