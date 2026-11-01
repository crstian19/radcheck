"""Run a model over a processed split and score it.

Backends:
  hf      load the model locally with transformers (optionally + a LoRA adapter)
  openai  any OpenAI-compatible server: llama-server, vLLM, ...

Usage:
    uv run --extra rocm python -m radcheck.evaluate --backend hf --model Qwen/Qwen3-0.6B \
        --data data/processed/test.jsonl --limit 200 --out outputs/eval/qwen3-0.6b-base.json
    uv run --extra rocm python -m radcheck.evaluate --backend hf --model Qwen/Qwen3-0.6B \
        --adapter outputs/train/qwen3-0.6b-lora --data data/processed/test.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

from radcheck.metrics import Scores
from radcheck.prompts import (
    CHAT_TEMPLATE_KWARGS,
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_EXTENDED,
    parse_output,
)


def _hf_generator(model_name: str, adapter: str | None, batch_size: int, max_new_tokens: int):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name, padding_side="left")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.bfloat16, attn_implementation="sdpa", device_map="cuda"
    )
    if adapter:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter)
    model.eval()

    def generate(prompts: list[list[dict]]) -> list[str]:
        outputs = []
        for i in range(0, len(prompts), batch_size):
            texts = [
                tok.apply_chat_template(
                    p, add_generation_prompt=True, tokenize=False, **CHAT_TEMPLATE_KWARGS
                )
                for p in prompts[i : i + batch_size]
            ]
            enc = tok(texts, return_tensors="pt", padding=True).to(model.device)
            with torch.no_grad():
                out = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False)
            outputs += tok.batch_decode(
                out[:, enc["input_ids"].shape[1] :], skip_special_tokens=True
            )
        return outputs

    return generate


def _openai_generator(
    model_name: str,
    base_url: str,
    max_new_tokens: int,
    template_kwargs: dict = CHAT_TEMPLATE_KWARGS,
    concurrency: int = 1,
):
    from concurrent.futures import ThreadPoolExecutor

    from openai import OpenAI

    client = OpenAI(base_url=base_url, api_key="unused", timeout=1800)

    def one(p: list[dict]) -> str:
        r = client.chat.completions.create(
            model=model_name,
            messages=p,
            temperature=0,
            max_tokens=max_new_tokens,
            extra_body={"chat_template_kwargs": template_kwargs},
        )
        return r.choices[0].message.content or ""

    def generate(prompts: list[list[dict]]) -> list[str]:
        # vLLM batches concurrent requests itself; map() keeps the input order.
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            return list(pool.map(one, prompts))

    return generate


def rescore(results: Path, data: Path) -> None:
    """Score the raw outputs stored in `results` again, with the current metric and gold."""
    saved = json.loads(results.read_text())
    with open(data, encoding="utf-8") as f:
        by_id = {ex["id"]: ex for ex in map(json.loads, f)}
    scores = Scores()
    for p in saved["predictions"]:
        ex = by_id[p["id"]]
        p["gold"], p["pred"] = ex["gold"], parse_output(p["raw"])
        scores.add(ex["prompt"][1]["content"], ex["gold"], p["pred"])
    saved["summary"] |= scores.summary()
    results.write_text(json.dumps(saved, indent=2, ensure_ascii=False))
    print(json.dumps(saved["summary"], indent=2, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--backend", choices=["hf", "openai"], default="hf")
    ap.add_argument("--model", help="required unless --rescore")
    ap.add_argument("--adapter", help="LoRA adapter directory (hf backend)")
    ap.add_argument("--base-url", default="http://localhost:8080/v1", help="openai backend")
    ap.add_argument("--data", default="data/processed/test.jsonl")
    ap.add_argument("--limit", type=int, help="random sample of N examples (seeded)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--max-new-tokens", type=int, default=256)
    ap.add_argument("--out", help="write metrics + predictions here (JSON)")
    ap.add_argument(
        "--system",
        choices=["data", "base", "extended"],
        default="data",
        help="system prompt: as stored in --data, or replace it (extended = recipe v3 types)",
    )
    ap.add_argument(
        "--thinking",
        action="store_true",
        help="let the model reason before answering (raise --max-new-tokens accordingly)",
    )
    ap.add_argument("--concurrency", type=int, default=1, help="parallel requests (openai)")
    ap.add_argument(
        "--rescore",
        metavar="RESULTS_JSON",
        help="re-score saved predictions against --data (after a metric or gold change)",
    )
    args = ap.parse_args()

    if args.rescore:
        rescore(Path(args.rescore), Path(args.data))
        return
    if not args.model:
        ap.error("--model is required")

    with open(args.data, encoding="utf-8") as f:
        examples = [json.loads(line) for line in f]
    if args.limit and args.limit < len(examples):
        examples = random.Random(args.seed).sample(examples, args.limit)

    if args.system != "data":
        system = SYSTEM_PROMPT_EXTENDED if args.system == "extended" else SYSTEM_PROMPT
        for ex in examples:
            ex["prompt"] = [{"role": "system", "content": system}, *ex["prompt"][1:]]

    if args.backend == "hf":
        generate = _hf_generator(args.model, args.adapter, args.batch_size, args.max_new_tokens)
    else:
        template_kwargs = {"enable_thinking": args.thinking}
        generate = _openai_generator(
            args.model, args.base_url, args.max_new_tokens, template_kwargs, args.concurrency
        )

    t0 = time.time()
    raw = generate([ex["prompt"] for ex in examples])
    elapsed = time.time() - t0

    scores = Scores()
    predictions = []
    for ex, text in zip(examples, raw):
        pred = parse_output(text)
        scores.add(ex["prompt"][1]["content"], ex["gold"], pred)
        predictions.append({"id": ex["id"], "gold": ex["gold"], "raw": text, "pred": pred})

    summary = scores.summary() | {
        "model": args.model,
        "adapter": args.adapter,
        "data": args.data,
        "thinking": args.thinking,
        "seconds": round(elapsed, 1),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(
            json.dumps(
                {"summary": summary, "predictions": predictions}, indent=2, ensure_ascii=False
            )
        )


if __name__ == "__main__":
    main()
