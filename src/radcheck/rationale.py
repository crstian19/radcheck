"""Add a short reasoning to every training answer, written by a teacher model (distillation).

discordancia stays at ~0.62 F1 for the 4B whatever the data, while Qwen3.8-27B reaches 0.67
when it reasons. Here the 27B writes, for each training example, the brief reasoning that
leads to the correct answer (it sees the gold errors: "rationalization"), and the answer
becomes {"analisis": "...", "errores": [...]}. The student learns to write the analysis
first, so it reasons a few sentences before committing to the errors. parse_output() only
needs the "errores" key, so evaluation works unchanged (raise --max-new-tokens).

Usage (server, vLLM venv):
    PYTHONPATH=src ~/radcheck-vllm/bin/python -m radcheck.rationale --data data/processed-v4 \
        --out data/processed-v4r
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

PROMPT = """Eres radiólogo y preparas ejemplos para enseñar a revisar informes.

Informe:
<<<
{report}
>>>

Errores reales de este informe (lista correcta, puede estar vacía):
{errors}

Escribe el razonamiento breve que lleva a esa respuesta, como si revisaras el informe tú mismo: compara lado, negaciones y medidas entre los hallazgos y la conclusión, comprueba si los hallazgos relevantes aparecen en la conclusión y busca palabras mal dictadas. Nombra solo lo que importa para la respuesta.
Máximo 3 frases y 70 palabras. No digas que conocías la respuesta. Responde solo con el razonamiento, sin JSON."""

MAX_CHARS = 600


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", default="Qwen/Qwen3.8-27B")
    ap.add_argument("--data", default="data/processed-v4")
    ap.add_argument("--out", default="data/processed-v4r")
    args = ap.parse_args()

    from vllm import LLM, SamplingParams

    data, out = Path(args.data), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    splits = {
        s: [json.loads(line) for line in (data / f"{s}.jsonl").read_text("utf-8").splitlines()]
        for s in ("train", "val")
    }
    jobs = [(s, i) for s, rows in splits.items() for i in range(len(rows))]
    answers = {(s, i): json.loads(splits[s][i]["completion"][0]["content"]) for s, i in jobs}
    conversations = [
        [
            {
                "role": "user",
                "content": PROMPT.format(
                    report=splits[s][i]["prompt"][-1]["content"],
                    errors=json.dumps(answers[s, i]["errores"], ensure_ascii=False, indent=1),
                ),
            }
        ]
        for s, i in jobs
    ]
    # Same Mamba-cache limit as synth.py: hybrid Qwen needs max_num_seqs <= ~576.
    llm = LLM(model=args.model, max_model_len=8192, gpu_memory_utilization=0.88, max_num_seqs=256)
    params = SamplingParams(temperature=0.3, top_p=0.95, max_tokens=200)
    outputs = llm.chat(
        conversations, params, chat_template_kwargs={"enable_thinking": False}, use_tqdm=True
    )

    counts = {"ok": 0, "fallback": 0}
    for (s, i), o in zip(jobs, outputs, strict=True):
        text = " ".join(o.outputs[0].text.split())
        if not text or len(text) > MAX_CHARS or "{" in text:
            counts["fallback"] += 1  # truncated or off-format: neutral sentence, same shape
            text = "Reviso lateralidad, negaciones, medidas, conclusión y dictado."
        else:
            counts["ok"] += 1
        ex = splits[s][i]
        ex["completion"] = [
            {
                "role": "assistant",
                "content": json.dumps({"analisis": text} | answers[s, i], ensure_ascii=False),
            }
        ]

    for s, rows in splits.items():
        with open(out / f"{s}.jsonl", "w", encoding="utf-8") as f:
            f.writelines(json.dumps(ex, ensure_ascii=False) + "\n" for ex in rows)
    shutil.copy(data / "test.jsonl", out / "test.jsonl")
    (out / "stats.json").write_text(json.dumps({"args": vars(args), **counts}, indent=2))
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
