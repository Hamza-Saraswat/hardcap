#!/usr/bin/env bash
# Test whether upgrading transformers unlocks Qwen3.6 in the Unsloth image; if the probe
# passes, bake the upgrade into a local image so every later run starts correct.
#
#   ./scripts/spark_build_image.sh          # probe only
#   ./scripts/spark_build_image.sh --build  # probe, then build hardcap-train:latest

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
MODELS_DIR="${MODELS_DIR:-$HOME/hardcap-work/models}"

# Two traps found in sequence here: the container's Python is PEP-668 "externally
# managed", so pip refuses to install anything without --break-system-packages (fine in
# a disposable container); and the installed unsloth pins transformers, so the trio has
# to move together. pip's output stays visible so a refusal can't masquerade as success.
UPGRADE="pip install --break-system-packages -U unsloth unsloth_zoo transformers 2>&1 | tail -3"

echo "=== probe: upgrade unsloth + transformers in a throwaway container ==="
docker run --rm --gpus all --entrypoint bash \
    -v "$MODELS_DIR":/models -e HF_HOME=/models \
    -v "$REPO/scripts":/probe \
    unsloth/unsloth:dgxspark-latest \
    -lc "$UPGRADE; python /probe/check_qwen_support.py"

if [ "${1:-}" != "--build" ]; then
    echo; echo "probe passed -- rerun with --build to bake the image"
    exit 0
fi

echo
echo "=== building hardcap-train:latest ==="
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf "$BUILD_DIR"' EXIT
cat > "$BUILD_DIR/Dockerfile" <<'EOF'
FROM unsloth/unsloth:dgxspark-latest
# The base image predates the Qwen3.6 architecture, and its unsloth pins transformers so
# neither can move alone. Upgrade the pure-Python trio together; torch / bitsandbytes /
# CUDA stay exactly as NVIDIA built them for GB10.
RUN pip install --no-cache-dir --break-system-packages -U unsloth unsloth_zoo transformers
EOF
docker build -t hardcap-train:latest "$BUILD_DIR"
echo
echo "built. train with:  TRAIN_IMAGE=hardcap-train:latest ./scripts/train_docker.sh ..."
