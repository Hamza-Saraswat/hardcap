#!/usr/bin/env bash
# Test whether upgrading transformers unlocks Qwen3.6 in the Unsloth image; if the probe
# passes, bake the upgrade into a local image so every later run starts correct.
#
#   ./scripts/spark_build_image.sh          # probe only
#   ./scripts/spark_build_image.sh --build  # probe, then build hardcap-train:latest

set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
MODELS_DIR="${MODELS_DIR:-$HOME/hardcap-work/models}"

echo "=== probe: upgrade transformers in a throwaway container ==="
docker run --rm --entrypoint bash \
    -v "$MODELS_DIR":/models -e HF_HOME=/models \
    -v "$REPO/scripts":/probe \
    unsloth/unsloth:dgxspark-latest \
    -lc "pip install -q -U transformers >/dev/null 2>&1; python /probe/check_qwen_support.py"

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
# The base image predates the Qwen3.6 architecture. Upgrade only the pure-Python layer;
# torch / bitsandbytes / CUDA stay exactly as NVIDIA and Unsloth pinned them for GB10.
RUN pip install --no-cache-dir -U transformers
EOF
docker build -t hardcap-train:latest "$BUILD_DIR"
echo
echo "built. train with:  TRAIN_IMAGE=hardcap-train:latest ./scripts/train_docker.sh ..."
