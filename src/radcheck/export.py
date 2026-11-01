"""Merge a LoRA adapter into its base model and export GGUF files for llama.cpp.

Usage:
    uv run --extra rocm python -m radcheck.export --model Qwen/Qwen3.5-4B \
        --adapter outputs/train/qwen35-4b-lora --name radcheck-qwen35-4b \
        --llama-cpp ~/Dev/llama.cpp --quants Q8_0 Q4_K_M

Writes models/<name>/merged (safetensors) and models/<name>/<name>-<quant>.gguf.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def merge(model: str, adapter: str, out: Path) -> None:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # CPU in bf16: no GPU memory needed, a 4B model takes a few minutes.
    base = AutoModelForCausalLM.from_pretrained(model, dtype=torch.bfloat16, device_map="cpu")
    merged = PeftModel.from_pretrained(base, adapter).merge_and_unload()
    merged.save_pretrained(out)
    # The adapter's tokenizer carries the chat template used in training.
    AutoTokenizer.from_pretrained(adapter).save_pretrained(out)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--llama-cpp", type=Path, default=Path.home() / "Dev/llama.cpp")
    ap.add_argument("--quants", nargs="+", default=["Q8_0", "Q4_K_M"])
    args = ap.parse_args()

    root = Path("models") / args.name
    merged = root / "merged"
    if not (merged / "config.json").exists():
        merge(args.model, args.adapter, merged)

    f16 = root / f"{args.name}-bf16.gguf"
    convert = args.llama_cpp / "convert_hf_to_gguf.py"
    # The converter ships its own `gguf` package; use it instead of a PyPI copy.
    env = os.environ | {"PYTHONPATH": str(args.llama_cpp / "gguf-py")}
    cmd = [sys.executable, convert, merged, "--outfile", f16, "--outtype", "bf16"]
    # Qwen3.5 declares a multi-token-prediction block that transformers neither loads nor
    # saves, so the merged model lacks its tensors: tell the converter to skip it.
    if json.loads((merged / "config.json").read_text()).get("mtp_num_hidden_layers"):
        cmd.append("--no-mtp")
    subprocess.run(
        cmd,
        check=True,
        env=env,
    )
    for q in args.quants:
        subprocess.run(
            [
                args.llama_cpp / "build/bin/llama-quantize",
                f16,
                root / f"{args.name}-{q}.gguf",
                q,
            ],
            check=True,
        )
    print(f"GGUF files in {root}")


if __name__ == "__main__":
    main()
