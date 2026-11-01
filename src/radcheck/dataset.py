"""Build the SFT dataset from CARES: split by report, then inject errors.

Usage:
    uv run --extra rocm python -m radcheck.dataset --cares data/raw/cares --out data/processed
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import re
from pathlib import Path

from datasets import load_from_disk

from radcheck.inject import (
    ALL_ERROR_TYPES,
    ERROR_TYPES,
    candidates,
    inject,
    inject_two,
    load_vocabulary,
    split_sections,
)
from radcheck.prompts import (
    CHAT_TEMPLATE_KWARGS,
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_EXTENDED,
    answer,
    prompt_messages,
)


def _split_of(report_id: int, val_fraction: float) -> str:
    """Deterministic train/val assignment from the report id (stable across runs)."""
    h = int(hashlib.sha256(str(report_id).encode()).hexdigest(), 16) % 10_000
    return "val" if h < val_fraction * 10_000 else "train"


def _gold(err) -> dict:
    return {
        "tipo": err.tipo,
        "fragmento": err.fragmento,
        "explicacion": err.explicacion,
        "start": err.start,
        "end": err.end,
        "original": err.original,
        "counterpart": list(err.counterpart) if err.counterpart else None,
    }


def _concat(a: dict, b: dict) -> dict:
    """Two examples pasted into one document; b's spans move past a's text."""
    ta, tb = a["prompt"][-1]["content"], b["prompt"][-1]["content"]
    offset = len(ta) + 2
    moved = []
    for g in b["gold"]:
        g = dict(g, start=g["start"] + offset, end=g["end"] + offset)
        if g["counterpart"]:
            g["counterpart"] = [g["counterpart"][0] + offset, g["counterpart"][1] + offset]
        moved.append(g)
    system = a["prompt"][0]["content"]
    return _example(a["report_id"], f"cat-{b['id']}", ta + "\n\n" + tb, a["gold"] + moved, system)


def _example(
    report_id: int | str, tag: str, report: str, gold: list[dict], system: str = SYSTEM_PROMPT
) -> dict:
    target = [{k: g[k] for k in ("tipo", "fragmento", "explicacion")} for g in gold]
    return {
        "id": f"{report_id}-{tag}",
        "report_id": report_id,
        "prompt": prompt_messages(report, system),
        "completion": [{"role": "assistant", "content": answer(target)}],
        "chat_template_kwargs": CHAT_TEMPLATE_KWARGS,
        "gold": gold,
    }


_SIDE_RE = re.compile(r"\b(derech|izquierd)[oa]s?\b", re.IGNORECASE)


def _mentions_both_sides(text: str) -> bool:
    return len({m.group(1).lower() for m in _SIDE_RE.finditer(text)}) == 2


def build_examples(
    reports: list[tuple[int, str]],
    rng: random.Random,
    variants: int,
    clean_ratio: float,
    recipe: str = "v1",
    hard_clean_share: float = 0.8,
) -> list[dict]:
    """Up to `variants` corrupted versions per eligible report, plus clean reports.

    Only ~40% of reports admit a verifiable error. Clean examples are therefore sampled
    from *all* reports (eligible or not) to reach `clean_ratio`, so "this report has no
    injectable pattern" is not a shortcut for "this report is clean".
    """
    reports = [(rid, text) for rid, text in reports if split_sections(text) is not None]
    # v3 = v2 + discordancia/transcripcion with the extended prompt.
    # v4 = v3 + documents with two errors (two in one report, or two reports pasted together).
    # v5 = v4 + a discordancia example for every report that admits one (more positives).
    extended = recipe in ("v3", "v4", "v5")
    multi = recipe in ("v4", "v5")
    types = ALL_ERROR_TYPES if extended else ERROR_TYPES
    system = SYSTEM_PROMPT_EXTENDED if extended else SYSTEM_PROMPT
    corrupted, seen = [], set()
    for report_id, text in reports:
        # v1: up to `variants` random draws (lateralidad dominates, ~64% of errors).
        # v2/v3: at most one variant per eligible error type, which balances the types.
        draws = [None] * variants if recipe == "v1" else sorted(candidates(text, rng, types))
        has_disc = "discordancia" in draws
        if extended:
            # Any long word admits a transcription slip, so it would be in every report and
            # crowd out the clean examples: keep it for ~30% and at most 2 types per report.
            if "transcripcion" in draws and rng.random() < 0.7:
                draws.remove("transcripcion")
            draws = sorted(rng.sample(draws, min(2, len(draws))))
        # Cleaning discordancia labels (v4c) lowered recall: the model needs more positives.
        if recipe == "v5" and has_disc and "discordancia" not in draws:
            draws.append("discordancia")
        for v, tipo in enumerate(draws):
            injected = inject(text, rng, tipo=tipo, types=types)
            if injected is None:
                break
            report, err = injected
            if report in seen:  # same candidate drawn twice
                continue
            seen.add(report)
            corrupted.append(_example(report_id, f"e{v}", report, [_gold(err)], system))
        # Robustness tests showed every model stops at one error per document.
        if multi and rng.random() < 0.25 and (two := inject_two(text, rng, types)):
            report, errs = two
            corrupted.append(_example(report_id, "e2x", report, [_gold(e) for e in errs], system))
    n_clean = min(len(reports), round(len(corrupted) * clean_ratio / (1 - clean_ratio)))
    if recipe == "v1":
        chosen = rng.sample(reports, n_clean)
    else:
        # Every lateralidad error mentions both sides, so "derecho and izquierdo both appear"
        # became a shortcut for "error" (main source of false alarms in v1). Draw clean
        # examples first from reports that mention both sides: hard negatives.
        hard = [r for r in reports if _mentions_both_sides(r[1])]
        easy = [r for r in reports if not _mentions_both_sides(r[1])]
        n_hard = min(len(hard), round(n_clean * hard_clean_share))
        chosen = rng.sample(hard, n_hard) + rng.sample(easy, min(len(easy), n_clean - n_hard))
    clean = [_example(rid, "clean", text, [], system) for rid, text in chosen]
    examples = corrupted + clean
    if multi:
        # ~8% pasted documents, any mix of corrupted and clean halves (clean + clean too,
        # so a long document is not a shortcut for "has errors").
        pool = list(examples)
        for _ in range(round(len(pool) * 0.08)):
            a, b = rng.sample(pool, 2)
            examples.append(_concat(a, b))
    rng.shuffle(examples)
    return examples


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--cares", default="data/raw/cares")
    ap.add_argument("--out", default="data/processed")
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--variants", type=int, default=3)
    ap.add_argument("--clean-ratio", type=float, default=0.5)
    ap.add_argument("--val-fraction", type=float, default=0.1)
    ap.add_argument(
        "--recipe", choices=["v1", "v2", "v3", "v4", "v5"], default="v1", help="see build_examples"
    )
    ap.add_argument(
        "--extra-reports",
        help="JSONL of extra clean reports ({id, text}), e.g. synthetic; added to train/val only",
    )
    ap.add_argument("--hard-clean-share", type=float, default=0.8, help="v2 only")
    args = ap.parse_args()

    cares = load_from_disk(args.cares)
    rng = random.Random(args.seed)
    splits: dict[str, list[tuple[int, str]]] = collections.defaultdict(list)
    for row in cares["train"]:
        splits[_split_of(row["id"], args.val_fraction)].append((row["id"], row["full_text"]))
    splits["test"] = [(row["id"], row["full_text"]) for row in cares["test"]]
    if args.extra_reports:
        with open(args.extra_reports, encoding="utf-8") as f:
            for row in map(json.loads, f):
                splits[_split_of(row["id"], args.val_fraction)].append((row["id"], row["text"]))
    # Transcription slips must produce words that never occur in real reports.
    load_vocabulary(text for rows in splits.values() for _, text in rows)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stats = {}
    for name in ("train", "val", "test"):
        examples = build_examples(
            splits[name], rng, args.variants, args.clean_ratio, args.recipe, args.hard_clean_share
        )
        with open(out / f"{name}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(ex, ensure_ascii=False) + "\n" for ex in examples)
        types = collections.Counter(g["tipo"] for ex in examples for g in ex["gold"])
        clean = sum(1 for ex in examples if not ex["gold"])
        stats[name] = {
            "reports": len(splits[name]),
            "examples": len(examples),
            "clean": clean,
            "clean_both_sides": sum(
                1
                for ex in examples
                if not ex["gold"] and _mentions_both_sides(ex["prompt"][1]["content"])
            ),
            **types,
        }
    (out / "stats.json").write_text(json.dumps({"args": vars(args), "splits": stats}, indent=2))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
