# Running on the DGX Spark

Development happens on the Mac; training and serving happen on the Spark. Copy the repo over
(`rsync -av --exclude .venv --exclude data ./ spark:~/capologist/`) along with
`data/dataset/`, then work from the Spark.

## 0. Host hygiene — do this before the first long run

The Spark's 128 GB is *unified* memory shared with the CPU, and exhausting it can take the
whole machine down rather than raising a clean CUDA OOM. Three cheap precautions:

```bash
sudo swapoff -a
```

```bash
sudo systemctl set-property user.slice MemoryMax=100G
```

Then keep an eye on it during the first run — if free memory collapses, kill the job rather
than letting the box swap itself to death:

```bash
watch -n 5 'free -g; nvidia-smi --query-gpu=memory.used,memory.total --format=csv'
```

There is also **no ECC** on the LPDDR5X. The training script checkpoints every 50 steps for
exactly this reason; don't raise that interval to speed things up.

## 1. Pull the container

Use NVIDIA's supported image. Bare-metal `pip install` on aarch64 + sm_121 is where people
lose days: PyTorch needs the cu130 index, Triton has misreported SM121 as SM80, and upstream
flash-attn has no ARM wheels at all.

```bash
docker pull unsloth/unsloth:dgxspark-latest
```

```bash
docker run --gpus all -it --rm \
  -v ~/capologist:/workspace \
  -w /workspace \
  --shm-size=16g \
  unsloth/unsloth:dgxspark-latest bash
```

## 2. Prototype run — gpt-oss-20b

Validate the whole loop cheaply before committing to a long run. Expect well under an hour
per epoch on a ~10k-example set.

```bash
python training/train_lora.py --preset prototype
```

Read the loss curve, then immediately score it — a prototype that trains cleanly but scores
badly usually means a data bug, not a hyperparameter one.

## 3. Main run — Qwen3.6-27B

```bash
python training/train_lora.py --preset main
```

Roughly 1–2 hours per epoch for ~10M tokens. If it OOMs, lower
`per_device_batch_size` before touching `max_seq_length` — memory scales super-linearly with
batch size, and shortening the context truncates the pasted cap sheets the model is supposed
to be reading.

Resume after an interruption:

```bash
python training/train_lora.py --preset main --resume
```

## 4. Export and serve

```bash
python serving/export.py --adapter outputs/main/adapter --preset main
```

That merges the adapter, writes a Q8_0 GGUF, and registers an Ollama model. Q8_0 rather than
Q4 is deliberate: this domain is arithmetic, and it's worth roughly half the tokens per
second to keep the fidelity.

## 5. Score it

```bash
python -m eval.harness --data data/dataset/eval.jsonl --model capologist --label "fine-tuned 27B"
```

Score the base model the same way for comparison. The fine-tune has to beat **both** the raw
base model and the base model handed the same context — if it doesn't beat the second, the
honest conclusion is that context was doing the work, and that belongs in the writeup.

## Gotchas worth knowing before you hit them

| Symptom | Cause | Fix |
|---|---|---|
| `libcudart.so.12` not found | PyPI PyTorch wheels are CUDA 12 | Use the container, or install from the cu130 index |
| `sm_121a is not defined` | ptxas version mismatch | `export TRITON_PTXAS_PATH=/usr/local/cuda/bin/ptxas` |
| Loss goes NaN | FP16 on GB10 | BF16 only — the script already forces this |
| flash-attn build fails | No aarch64 wheels, CUDA 13 linkage | Don't install it; SDPA is faster here anyway |
| Whole machine freezes | Unified-memory exhaustion | swapoff, cgroup cap, smaller batch |
| "sm_121 exceeds max supported" warning | Benign | sm_120 and sm_121 are binary compatible |
