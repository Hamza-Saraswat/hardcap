# DGX Spark Fine-Tuning Stack — Research Notes

Research date: 2026-07-28. Drives every decision in `training/` and `serving/`.

## Hardware envelope

GB10 Grace Blackwell: 128 GB unified LPDDR5x @ **273 GB/s**, ~100 TFLOPS BF16 measured (~1 PFLOP FP4
sparse peak), 20-core ARM CPU, 4 TB NVMe, ConnectX-7, DGX OS 7.4 (Ubuntu 24.04), CUDA 13.x,
compute capability **sm_121**. $4,699 since Feb 2026.

**It is a capacity machine, not a speed machine.** Prefill is strong (2k–8k tok/s — good for our long
pasted cap sheets); decode is bandwidth-bound. Rule of thumb: `decode tok/s ≈ 273 ÷ model GB`, at
70–85% efficiency. MoE models are disproportionately good here since only active experts are read.

**No ECC on LPDDR5x** → checkpoint frequently on long runs.

## What fits

| Technique | Comfortable | Ceiling |
|---|---|---|
| Full fine-tune | ≤3–4B | ~8B (tight) |
| LoRA (BF16 base) | 7B–32B | 70B |
| QLoRA (4-bit) | 20B–70B | gpt-oss-120b (~68 GB) |

NVIDIA's conservative published throughputs: Llama 3.2 3B full FT 13,519 tok/s; Llama 3.1 8B LoRA
6,970 tok/s; Llama 3.3 70B QLoRA 760 tok/s (bs 4–8, seq 2048).
⚠️ A second "peak" figure set circulates (~6–7× higher) from the same launch material — plan with the
lower numbers. ([NVIDIA blog, Oct 2025](https://developer.nvidia.com/blog/how-nvidia-dgx-sparks-performance-enables-intensive-ai-tasks))

Estimated epoch times for our ~10M-token dataset: gpt-oss-20b QLoRA well under an hour; 27B LoRA
~1–2 h; 70B QLoRA ~3.7 h.

## Framework decision: Unsloth via the official DGX Spark Docker image

`unsloth/unsloth:dgxspark-latest` — built on NGC PyTorch with pinned bitsandbytes/transformers/trl.
**Use containers, never bare-metal pip.** Unsloth is NVIDIA's flagship Spark fine-tuning playbook
([build.nvidia.com/spark/unsloth](https://build.nvidia.com/spark/unsloth) ·
[Unsloth guide](https://unsloth.ai/docs/blog/fine-tuning-llms-with-nvidia-dgx-spark-and-unsloth)).

Other supported paths: NVIDIA's PyTorch/PEFT playbook (also covers dual-Spark FSDP to 70B),
LLaMA-Factory, NeMo AutoModel. **Not viable on Spark as of mid-2026:** Axolotl, torchtune (no
documented sm_121 support).

### Gotchas (all verified in community reports)
- **Skip upstream flash-attn** — no aarch64 wheels, CUDA-12 linkage breaks on CUDA 13. Use
  `attn_implementation="sdpa"` (reportedly faster on Blackwell anyway) or the FA2 inside NGC images.
- **BF16, never FP16** — FP16 GPU inference produced inf/NaN on GB10.
- **Unified-memory OOM can take down the whole box** ("swap death spiral"). Disable swap, set a
  cgroup memory cap (~100 GB), run an OOM watchdog.
  ([natolambert/dgx-spark-setup](https://github.com/natolambert/dgx-spark-setup))
- Memory scales **super-linearly with batch size** (Qwen3-0.6B SFT: bs=8/seq1024 → 47 GB;
  bs=16 → 81 GB). Prefer grad accumulation over big batches.
- PyTorch must come from the **cu130** index on aarch64; `TRITON_PTXAS_PATH` workaround for
  "sm_121a is not defined" ptxas errors.

## Base model selection

| Model | Params | License | Why / why not |
|---|---|---|---|
| **Qwen3.6-27B dense** ⭐ final | 27B | Apache 2.0 | Best open reasoning-per-param (Artificial Analysis index 37 vs gpt-oss-20b's 15), 262K context, Apr 2026. Fits BF16 LoRA. Serving ~12–14 t/s at Q4. |
| **gpt-oss-20b** ⭐ prototype | 21B-A3.6B MoE | Apache 2.0 | The official Spark playbook model; native MXFP4; fastest loop (58–82 t/s serving). Must train in **harmony** chat format. Lower reasoning ceiling. |
| gpt-oss-120b | 117B-A5.1B | Apache 2.0 | QLoRA at ~68 GB; serves 35–55 t/s *faster than the dense 27B* thanks to MoE. Fallback ceiling. |
| Qwen3.6-35B-A3B | 35B-A3B MoE | Apache 2.0 | Best serving speed/quality balance (~28–32 t/s). MoE LoRA is finickier to train. Good v2 target. |
| Gemma 4 31B | 31B | Apache 2.0 | Credible alternative, Apr 2026, day-one Unsloth support. Less evidence on table-heavy math. |
| Nemotron 3 Nano | 31.6B-A3.6B | NVIDIA Open | Has a Spark playbook + thinking-budget control; hybrid Mamba needs extra deps. |
| Llama 3.3 70B / Llama 4 | — | Llama | Skip — older generation, slower, beaten by 2026 27–35B models. No new open Llama in 2026. |

Everything ≥280B (DeepSeek V4, GLM-5, Kimi K3) does not fit.

## Serving

Unsloth exports merged LoRA → GGUF / vLLM-ready HF / Ollama Modelfile. **llama.cpp + Ollama is the
most reliable path on Spark** (day-one support; a Jan 2026 collab added ~35% for MoE models). vLLM
works only via NGC containers (`nvcr.io/nvidia/vllm:26.0x-py3`) — upstream wheels still lack sm_121
aarch64 support. TensorRT-LLM gives the best prefill and NVFP4 quantization.

**We use Q8_0 GGUF + Ollama** — roughly half the speed of Q4 but preserves arithmetic fidelity, which
this domain requires.
