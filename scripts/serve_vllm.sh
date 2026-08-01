#!/usr/bin/env bash
# Serve a model with the NGC vLLM container on the Spark (OpenAI-compatible on :8000).
#
#   ./scripts/serve_vllm.sh unsloth/Qwen3.6-27B qwen-base          # baseline eval
#   ./scripts/serve_vllm.sh /workspace/outputs/main/merged capologist   # fine-tuned
#
# Notes specific to this box:
#   - The NGC image is the supported sm_121 path; upstream wheels still aren't.
#   - GPU "memory" here is the unified 121GB pool. vLLM's default grabs 90% of it,
#     which starves everything else on the machine -- so utilization is capped and
#     context length is bounded to what the eval actually needs.

set -euo pipefail

MODEL="${1:?usage: serve_vllm.sh <hf-id-or-path> [served-name] [port]}"
NAME="${2:-model}"
PORT="${3:-8000}"
MODELS_DIR="${MODELS_DIR:-$HOME/hardcap-work/models}"
IMAGE="${VLLM_IMAGE:-nvcr.io/nvidia/vllm:26.05.post1-py3}"

exec docker run --rm --gpus all -p "$PORT:8000" \
    -v "$MODELS_DIR":/models -e HF_HOME=/models \
    -v "$HOME/hardcap":/workspace \
    --shm-size=16g \
    "$IMAGE" \
    vllm serve "$MODEL" \
        --served-model-name "$NAME" \
        --max-model-len 8192 \
        --gpu-memory-utilization 0.60 \
        --port 8000
