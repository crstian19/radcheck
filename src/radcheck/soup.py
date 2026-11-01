"""Average several LoRA adapters of the same base model into one ("model soup").

Adapters trained with different seeds land in slightly different places; averaging their
weight deltas often keeps what they share and cancels part of the seed noise. PEFT's "cat"
combination is exact: the new adapter stacks every A and B, so its delta is
sum(w_i * scaling_i * B_i @ A_i). With w_i = 1/n that is the mean delta, at rank sum(r_i).

Usage (server):
    uv run --extra cuda python -m radcheck.soup --model Qwen/Qwen3.5-4B \
        --adapters outputs/train/qwen35-4b-v4 outputs/train/qwen35-4b-v4-s7 \
        outputs/train/qwen35-4b-v4-s13 --out outputs/train/qwen35-4b-v4-soup
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapters", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM

    # CPU is enough: no forward pass, only adapter arithmetic.
    base = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.bfloat16)
    names = [f"a{i}" for i in range(len(args.adapters))]
    model = PeftModel.from_pretrained(base, args.adapters[0], adapter_name=names[0])
    for name, path in zip(names[1:], args.adapters[1:]):
        model.load_adapter(path, adapter_name=name)
    weights = [1 / len(names)] * len(names)
    model.add_weighted_adapter(names, weights, "soup", combination_type="cat")

    # Check on one layer that the soup delta is the mean of the individual deltas.
    layer = next(m for m in model.modules() if hasattr(m, "lora_A") and "soup" in m.lora_A)

    def delta(n: str) -> torch.Tensor:
        a, b = layer.lora_A[n].weight.float(), layer.lora_B[n].weight.float()
        return layer.scaling[n] * b @ a

    expected = sum(w * delta(n) for n, w in zip(names, weights))
    err = (delta("soup") - expected).abs().max().item() / expected.abs().max().item()
    print(f"soup check: max relative error {err:.2e}")
    assert err < 1e-2, "soup delta is not the mean of the adapters"

    tmp = Path(args.out + ".tmp")
    model.save_pretrained(tmp, selected_adapters=["soup"])
    # PEFT writes non-default adapters into a subfolder named after them.
    src = tmp / "soup" if (tmp / "soup").is_dir() else tmp
    shutil.rmtree(args.out, ignore_errors=True)
    shutil.move(src, args.out)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"saved {args.out}")


if __name__ == "__main__":
    main()
