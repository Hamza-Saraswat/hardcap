"""Can this environment load the Qwen3.6 architecture? Run inside the training container.

Exits nonzero with the real error if not -- used to validate a transformers upgrade before
baking it into an image.
"""

import sys

import transformers

print("transformers:", transformers.__version__)

from transformers import AutoConfig, AutoTokenizer

config = AutoConfig.from_pretrained("unsloth/Qwen3.6-27B")
print("architecture:", config.model_type)

tokenizer = AutoTokenizer.from_pretrained("unsloth/Qwen3.6-27B")
probe = tokenizer.apply_chat_template(
    [{"role": "user", "content": "ping"}], tokenize=False, add_generation_prompt=True
)
print("chat template renders:", len(probe), "chars")

try:
    import unsloth  # noqa: F401

    print("unsloth imports alongside upgraded transformers")
except Exception as exc:  # noqa: BLE001
    print("UNSLOTH BROKE:", exc)
    sys.exit(2)

print("OK")
