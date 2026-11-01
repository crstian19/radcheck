"""Binary "decision" model: does this report contain an error? (clean vs error)

A small encoder (mmBERT, MrBERT, bsc-bio-ehr-es, ...) fine-tuned as a sequence classifier.
It cannot say *where* the error is; the idea is a fast first pass in front of the LLM
(only reports it flags, or is unsure about, go to the LLM) or a verifier after it.

Usage:
    uv run --extra rocm python -m radcheck.classifier --model jhu-clsp/mmBERT-base \
        --data data/processed-v3 --bench bench/radcheck_bench_v1_test.jsonl \
        --output outputs/clf/mmbert-base --max-length 1024

Writes metrics.json: accuracy, detection rate, false alarm rate, ECE before and after
temperature scaling (fitted on val), and throughput, for val, test and the benchmark.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)


def load_split(path: Path) -> Dataset:
    """Report text and label (1 = has at least one error) from radcheck's JSONL format."""
    rows = [json.loads(line) for line in path.open(encoding="utf-8")]
    return Dataset.from_dict(
        {
            "text": [r["prompt"][-1]["content"] for r in rows],
            "label": [int(bool(r["gold"])) for r in rows],
        }
    )


def ece(probs: np.ndarray, labels: np.ndarray, bins: int = 10) -> float:
    """Expected calibration error of P(error): |accuracy - confidence| averaged over bins."""
    conf = np.where(probs >= 0.5, probs, 1 - probs)
    correct = (probs >= 0.5).astype(int) == labels
    edges = np.linspace(0.5, 1.0, bins + 1)
    total = 0.0
    for lo, hi in itertools.pairwise(edges):
        mask = (conf > lo) & (conf <= hi)
        if mask.any():
            total += mask.mean() * abs(correct[mask].mean() - conf[mask].mean())
    return float(total)


def fit_temperature(logits: np.ndarray, labels: np.ndarray) -> float:
    """One temperature minimising validation log-loss (grid search, good enough here)."""
    best_t, best_loss = 1.0, float("inf")
    for t in np.linspace(0.25, 5.0, 96):
        logp = torch.log_softmax(torch.tensor(logits) / t, dim=-1).numpy()
        loss = -logp[np.arange(len(labels)), labels].mean()
        if loss < best_loss:
            best_t, best_loss = float(t), float(loss)
    return best_t


def scores(logits: np.ndarray, labels: np.ndarray, temperature: float) -> dict:
    probs = torch.softmax(torch.tensor(logits) / temperature, dim=-1)[:, 1].numpy()
    raw = torch.softmax(torch.tensor(logits), dim=-1)[:, 1].numpy()
    pred = (probs >= 0.5).astype(int)
    errors, clean = labels == 1, labels == 0
    return {
        "examples": len(labels),
        "accuracy": round(float((pred == labels).mean()), 3),
        "detection_rate": round(float(pred[errors].mean()), 3) if errors.any() else None,
        "false_alarm_rate": round(float(pred[clean].mean()), 3) if clean.any() else None,
        "ece_raw": round(ece(raw, labels), 3),
        "ece_calibrated": round(ece(probs, labels), 3),
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", default="data/processed-v3")
    ap.add_argument("--bench", default="bench/radcheck_bench_v1_test.jsonl")
    ap.add_argument("--output", required=True)
    ap.add_argument("--max-length", type=int, default=1024)
    ap.add_argument("--epochs", type=float, default=2)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--grad-accum", type=int, default=2)
    args = ap.parse_args()

    tok = AutoTokenizer.from_pretrained(args.model)
    # fp32 weights + bf16 autocast (mixed precision): a ~300M model fits, and the optimizer
    # keeps full-precision updates.
    model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=2)

    def encode(ds: Dataset) -> Dataset:
        return ds.map(
            lambda b: tok(b["text"], truncation=True, max_length=args.max_length),
            batched=True,
            remove_columns=["text"],
        )

    data = Path(args.data)
    splits = {name: load_split(data / f"{name}.jsonl") for name in ("train", "val", "test")}
    splits["bench"] = load_split(Path(args.bench))
    encoded = {name: encode(ds) for name, ds in splits.items()}
    truncated = {
        name: round(float(np.mean([len(x) >= args.max_length for x in ds["input_ids"]])), 3)
        for name, ds in encoded.items()
    }

    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=args.output,
            num_train_epochs=args.epochs,
            learning_rate=args.lr,
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=args.batch_size * 2,
            gradient_accumulation_steps=args.grad_accum,
            # 1,024-token reports on a 16 GB card: recompute activations instead of storing them.
            gradient_checkpointing=True,
            warmup_steps=0.1,
            weight_decay=0.01,
            bf16=True,
            eval_strategy="epoch",
            save_strategy="no",
            logging_steps=50,
            report_to="tensorboard",
        ),
        train_dataset=encoded["train"],
        eval_dataset=encoded["val"],
        processing_class=tok,
    )
    t0 = time.time()
    trainer.train()
    train_seconds = time.time() - t0

    results: dict = {"model": args.model, "max_length": args.max_length, "truncated": truncated}
    outputs = {}
    for name in ("val", "test", "bench"):
        t0 = time.time()
        pred = trainer.predict(encoded[name])
        outputs[name] = (pred.predictions.astype(np.float32), np.array(pred.label_ids))
        results[f"{name}_ms_per_report"] = round(1000 * (time.time() - t0) / len(encoded[name]), 1)
    temperature = fit_temperature(*outputs["val"])
    results["temperature"] = round(temperature, 2)
    for name, (logits, labels) in outputs.items():
        results[name] = scores(logits, labels, temperature)
    results["train_seconds"] = round(train_seconds)

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(results, indent=2))
    np.save(out / "bench_logits.npy", outputs["bench"][0])
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
