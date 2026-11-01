"""Reasoning distillation with rejection sampling: keep only analyses that reach the right answer.

v4r failed because the 27B wrote each analysis *knowing* the answer: post-hoc explanations
that always agree with the label, so the student learned to sound sure, not to be right.
Here the 27B sees only the report (as the student will), writes a short analysis and its own
answer, and an example is kept only when that answer matches the gold errors exactly. The
kept completion is {"analisis": <teacher's analysis>, "errores": <gold errors>}; examples
the teacher gets wrong are dropped (stats.json says how many, per type).

Usage (server, vLLM venv):
    PYTHONPATH=src ~/radcheck-vllm/bin/python -m radcheck.distill --data data/processed-v4 \
        --out data/processed-v4d
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path

from radcheck.metrics import _matches
from radcheck.prompts import parse_output

SUFFIX = """

Antes de la lista, razona en el campo "analisis" (máximo 3 frases y 70 palabras): compara lado, negaciones y medidas entre los hallazgos y la conclusión, comprueba si los hallazgos relevantes aparecen en la conclusión y busca palabras mal dictadas.
Formato: {"analisis": "...", "errores": [...]}"""


def exact(pred: list[dict] | None, gold: list[dict], report: str) -> bool:
    """Every gold error found once, and nothing else flagged."""
    if pred is None or len(pred) != len(gold):
        return False
    unmatched = list(gold)
    for p in pred:
        hit = next((g for g in unmatched if _matches(p, g, report)), None)
        if hit is None:
            return False
        unmatched.remove(hit)
    return True


def analysis(text: str) -> str | None:
    """The teacher's "analisis" field, if the answer is a JSON object that has one."""
    start = text.find("{")
    try:
        obj, _ = json.JSONDecoder().raw_decode(text, start) if start != -1 else (None, 0)
    except json.JSONDecodeError:
        return None
    a = obj.get("analisis") if isinstance(obj, dict) else None
    return " ".join(a.split()) if isinstance(a, str) and 0 < len(a) <= 600 else None


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", default="Qwen/Qwen3.8-27B")
    ap.add_argument("--data", default="data/processed-v4")
    ap.add_argument("--out", default="data/processed-v4d")
    ap.add_argument("--samples", type=int, default=2, help="tries per example")
    ap.add_argument("--limit", type=int, help="first N examples per split (smoke test)")
    args = ap.parse_args()

    from vllm import LLM, SamplingParams

    data, out = Path(args.data), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    splits = {
        s: [json.loads(line) for line in (data / f"{s}.jsonl").read_text("utf-8").splitlines()][
            : args.limit
        ]
        for s in ("train", "val")
    }
    jobs = [(s, i) for s, rows in splits.items() for i in range(len(rows))]
    conversations = []
    for s, i in jobs:
        system, user = splits[s][i]["prompt"][0], splits[s][i]["prompt"][-1]
        conversations.append(
            [{"role": "system", "content": system["content"] + SUFFIX}, dict(user)]
        )
    # Same Mamba-cache limit as synth.py: hybrid Qwen needs max_num_seqs <= ~576.
    llm = LLM(model=args.model, max_model_len=8192, gpu_memory_utilization=0.88, max_num_seqs=256)
    params = SamplingParams(n=args.samples, temperature=0.7, top_p=0.95, max_tokens=512)
    outputs = llm.chat(
        conversations, params, chat_template_kwargs={"enable_thinking": False}, use_tqdm=True
    )

    kept: dict[str, list[dict]] = {s: [] for s in splits}
    total, ok = Counter(), Counter()
    for (s, i), o in zip(jobs, outputs, strict=True):
        ex = splits[s][i]
        report, gold = ex["prompt"][-1]["content"], ex["gold"]
        types = sorted({g["tipo"] for g in gold}) or ["limpio"]
        for t in types:
            total[t] += 1
        for c in o.outputs:
            a = analysis(c.text)
            if a and exact(parse_output(c.text), gold, report):
                answer = json.loads(ex["completion"][0]["content"])
                ex["completion"] = [
                    {
                        "role": "assistant",
                        "content": json.dumps({"analisis": a} | answer, ensure_ascii=False),
                    }
                ]
                kept[s].append(ex)
                for t in types:
                    ok[t] += 1
                break

    for s, rows in kept.items():
        with open(out / f"{s}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(ex, ensure_ascii=False) + "\n" for ex in rows)
    shutil.copy(data / "test.jsonl", out / "test.jsonl")
    stats = {
        "args": vars(args),
        "kept": {s: len(rows) for s, rows in kept.items()},
        "of": {s: len(rows) for s, rows in splits.items()},
        "keep_rate_by_type": {t: round(ok[t] / total[t], 3) for t in sorted(total)},
    }
    (out / "stats.json").write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
