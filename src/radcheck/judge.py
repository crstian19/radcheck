"""Clean the discordancia labels with an LLM judge (vLLM, Qwen3.8-27B with reasoning).

discordancia is the weak type (F1 ~0.4 on the injector test for every model, 4B or 27B),
while the 27B reasoning model scores 0.67 on the independent benchmark. That pattern points
at label noise: the injector drops a conclusion sentence, but the conclusion may still cover
the finding in other words, or the finding may be too minor to belong in a conclusion. In
both cases "missing from the conclusion" is not a real error and the label teaches noise.

The judge sees the corrupted report and the flagged finding and answers two questions. An
example is kept only if the finding is relevant and the conclusion no longer covers it.
Examples without discordancia are copied unchanged; the test split is never touched.

Usage (server, vLLM venv):
    PYTHONPATH=src ~/radcheck-vllm/bin/python -m radcheck.judge --data data/processed-v4 \
        --out data/processed-v4c
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

PROMPT = """Eres radiólogo y revisas la calidad de un conjunto de datos.

Informe:
<<<
{report}
>>>

Hallazgo de la sección HALLAZGOS: «{fragment}»

Responde a dos preguntas sobre el informe tal y como está:
1. "cubierto": ¿la CONCLUSIÓN menciona ese hallazgo, aunque sea con otras palabras o englobado en otro diagnóstico?
2. "relevante": ¿es un hallazgo que un radiólogo esperaría ver en la conclusión (patológico o clínicamente significativo, no un hallazgo normal o banal)?

Responde solo con JSON: {{"cubierto": true|false, "relevante": true|false}}"""

_JSON_RE = re.compile(r"\{[^{}]*\"cubierto\"[^{}]*\}")


def parse(text: str) -> dict | None:
    """Last JSON object with the expected keys, after the reasoning block if any."""
    text = text.rsplit("</think>", 1)[-1]
    for m in reversed(_JSON_RE.findall(text)):
        try:
            d = json.loads(m)
        except json.JSONDecodeError:
            continue
        if isinstance(d.get("cubierto"), bool) and isinstance(d.get("relevante"), bool):
            return d
    return None


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", default="Qwen/Qwen3.8-27B")
    ap.add_argument("--data", default="data/processed-v4")
    ap.add_argument("--out", default="data/processed-v4c")
    ap.add_argument("--max-tokens", type=int, default=4096)
    args = ap.parse_args()

    from vllm import LLM, SamplingParams

    data, out = Path(args.data), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    splits = {
        s: [json.loads(line) for line in (data / f"{s}.jsonl").read_text("utf-8").splitlines()]
        for s in ("train", "val")
    }
    jobs = [  # (split, example index, gold index)
        (s, i, j)
        for s, rows in splits.items()
        for i, ex in enumerate(rows)
        for j, g in enumerate(ex["gold"])
        if g["tipo"] == "discordancia"
    ]
    conversations = [
        [
            {
                "role": "user",
                "content": PROMPT.format(
                    report=splits[s][i]["prompt"][-1]["content"],
                    fragment=splits[s][i]["gold"][j]["fragmento"],
                ),
            }
        ]
        for s, i, j in jobs
    ]
    # Same Mamba-cache limit as synth.py: hybrid Qwen needs max_num_seqs <= ~576.
    llm = LLM(model=args.model, max_model_len=8192, gpu_memory_utilization=0.88, max_num_seqs=256)
    params = SamplingParams(temperature=0.6, top_p=0.95, max_tokens=args.max_tokens)
    outputs = llm.chat(
        conversations, params, chat_template_kwargs={"enable_thinking": True}, use_tqdm=True
    )

    verdicts, drop = [], set()
    counts = {"kept": 0, "covered": 0, "not_relevant": 0, "unparsed": 0}
    for (s, i, j), o in zip(jobs, outputs, strict=True):
        v = parse(o.outputs[0].text)
        ex = splits[s][i]
        if v is None:
            counts["unparsed"] += 1  # no verdict: keep the example as it was
        elif v["cubierto"]:
            counts["covered"] += 1
            drop.add((s, i))
        elif not v["relevante"]:
            counts["not_relevant"] += 1
            drop.add((s, i))
        else:
            counts["kept"] += 1
        verdicts.append({"split": s, "id": ex["id"], "fragmento": ex["gold"][j]["fragmento"],
                         "verdict": v})  # fmt: skip

    for s, rows in splits.items():
        kept = [ex for i, ex in enumerate(rows) if (s, i) not in drop]
        with open(out / f"{s}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(ex, ensure_ascii=False) + "\n" for ex in kept)
        counts[f"{s}_examples"] = f"{len(rows)} -> {len(kept)}"
    shutil.copy(data / "test.jsonl", out / "test.jsonl")
    with open(out / "judge.jsonl", "w", encoding="utf-8") as f:
        f.writelines(json.dumps(v, ensure_ascii=False) + "\n" for v in verdicts)
    (out / "stats.json").write_text(json.dumps({"args": vars(args), **counts}, indent=2))
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
