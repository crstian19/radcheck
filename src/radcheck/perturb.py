"""Robustness variants of an evaluation file: same reports, messier text.

Real reports are not as tidy as the benchmark. Each variant keeps the labelled errors and
moves their character spans so the usual metric still applies:

- lower      everything lowercase (dictation systems often drop case)
- noheaders  section headers removed (HALLAZGOS:, CONCLUSIÓN:, ...): one run-on text
- typos      dictation slips in ~10% of the long words outside the labelled spans
- pairs      two reports pasted as one document (two errors, or one error + a clean report)

Usage:
    uv run --extra rocm python -m radcheck.perturb --data bench/radcheck_bench_v1_test.jsonl \
        --out bench/robustness
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from radcheck.inject import _SLIPS

_HEADER_RE = re.compile(
    r"\b(?:EXPLORACI[OÓ]N(?:ES)?|T[EÉ]CNICA|HALLAZGOS|CONCLUSI[OÓ]N(?:ES)?|"
    r"IMPRESI[OÓ]N(?: DIAGN[OÓ]STICA)?|INFORMACI[OÓ]N CL[IÍ]NICA)\s*:\s*"
)


def _spans(gold: list[dict]) -> list[tuple[int, int]]:
    out = []
    for g in gold:
        out.append((g["start"], g["end"]))
        if g.get("counterpart"):
            out.append(tuple(g["counterpart"]))
    return out


def _apply(text: str, gold: list[dict], edits: list[tuple[int, int, str]]):
    """Apply non-overlapping (start, end, replacement) edits and move the gold spans."""
    protected = _spans(gold)
    edits = sorted(e for e in edits if not any(e[0] < b and a < e[1] for a, b in protected))
    out, pos, shifts = [], 0, []
    for start, end, repl in edits:
        out += [text[pos:start], repl]
        shifts.append((end, len(repl) - (end - start)))
        pos = end
    out.append(text[pos:])

    def move(p: int) -> int:
        return p + sum(d for at, d in shifts if at <= p)

    new_gold = []
    for g in gold:
        g = dict(g)
        g["start"], g["end"] = move(g["start"]), move(g["end"])
        if g.get("counterpart"):
            g["counterpart"] = [move(g["counterpart"][0]), move(g["counterpart"][1])]
        new_gold.append(g)
    return "".join(out), new_gold


def lower(text, gold, rng):
    return text.lower(), gold


def noheaders(text, gold, rng):
    return _apply(text, gold, [(m.start(), m.end(), "") for m in _HEADER_RE.finditer(text)])


def typos(text, gold, rng):
    edits = []
    for m in re.finditer(r"\b[a-záéíóúñ]{7,}\b", text):
        if rng.random() > 0.10:
            continue
        word = m.group()
        slips = [(p, r) for p, r in _SLIPS if p.search(word)]
        if slips:
            p, r = rng.choice(slips)
            h = rng.choice(list(p.finditer(word)))
            edits.append((m.start(), m.end(), word[: h.start()] + h.expand(r) + word[h.end() :]))
    return _apply(text, gold, edits)


def with_report(ex: dict, text: str, gold: list[dict], tag: str) -> dict:
    ex = json.loads(json.dumps(ex))
    ex["id"] = f"{ex['id']}-{tag}"
    ex["prompt"][-1]["content"] = text
    ex["gold"] = gold
    return ex


def pairs(examples: list[dict], rng: random.Random) -> list[dict]:
    """Error + error and error + clean documents, the second report shifted after the first."""
    errs = [e for e in examples if e["gold"]]
    clean = [e for e in examples if not e["gold"]]
    rng.shuffle(errs)
    rng.shuffle(clean)
    out = []
    for i in range(0, len(errs) - 1, 2):
        a, b = errs[i], (errs[i + 1] if i // 2 % 2 == 0 else clean[i // 2 % len(clean)])
        ta, tb = a["prompt"][-1]["content"], b["prompt"][-1]["content"]
        sep = "\n\n"
        offset = len(ta) + len(sep)
        moved = []
        for g in b["gold"]:
            g = dict(g)
            g["start"] += offset
            g["end"] += offset
            if g.get("counterpart"):
                g["counterpart"] = [g["counterpart"][0] + offset, g["counterpart"][1] + offset]
            moved.append(g)
        out.append(with_report(a, ta + sep + tb, a["gold"] + moved, f"pair-{b['id']}"))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--data", default="bench/radcheck_bench_v1_test.jsonl")
    ap.add_argument("--out", default="bench/robustness")
    ap.add_argument("--seed", type=int, default=13)
    args = ap.parse_args()

    examples = [json.loads(line) for line in open(args.data, encoding="utf-8")]  # noqa: SIM115
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("lower", lower), ("noheaders", noheaders), ("typos", typos)):
        rng = random.Random(args.seed)
        rows = []
        for ex in examples:
            text, gold = fn(ex["prompt"][-1]["content"], ex["gold"], rng)
            rows.append(with_report(ex, text, gold, name))
        _write(out / f"{name}.jsonl", rows)
    _write(out / "pairs.jsonl", pairs(examples, random.Random(args.seed)))


def _write(path: Path, rows: list[dict]) -> None:
    # Every gold span must still point at the same text it pointed at before.
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(f"{path}: {len(rows)} reports, {sum(len(r['gold']) for r in rows)} errors")


if __name__ == "__main__":
    main()
