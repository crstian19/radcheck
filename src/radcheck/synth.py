"""Generate synthetic *clean* Spanish radiology reports with a local LLM (vLLM).

They widen the training distribution beyond CARES (one hospital, one style). Errors are
injected afterwards by the same rule-based injector, so the reports only need to be clean
and to repeat key facts (side, measure, negated finding) in findings and conclusion.

Never use RadCheck-Bench-ES prompts or items here: the benchmark must stay independent.

Usage (needs a CUDA box and a separate venv with vLLM):
    ~/radcheck-vllm/bin/python -m radcheck.synth --model Qwen/Qwen3.8-27B-FP8 \
        --n 4000 --out data/synthetic/reports.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path

from radcheck.inject import split_sections

MODALITIES = {
    "RX": ["tórax", "abdomen", "columna lumbar", "rodilla", "hombro", "cadera", "mano"],
    "TC": ["tórax", "abdomen y pelvis", "cráneo", "columna", "senos paranasales", "cuello"],
    "RM": ["cerebral", "columna lumbar", "columna cervical", "rodilla", "hombro", "pelvis"],
    "Ecografía": ["abdominal", "renal", "tiroidea", "de partes blandas", "escrotal", "mamaria"],
    "Mamografía": ["bilateral de cribado", "diagnóstica"],
}
STYLES = {
    "secciones": "Usa las cabeceras en mayúsculas EXPLORACIÓN:, HALLAZGOS: y CONCLUSIÓN: "
    "en un único párrafo por sección.",
    "lista": "Usa las cabeceras HALLAZGOS: y CONCLUSIÓN: y escribe los hallazgos como lista "
    "con guiones, uno por línea.",
    "narrativo": "Escribe los hallazgos en prosa narrativa larga bajo HALLAZGOS: y termina con "
    "IMPRESIÓN DIAGNÓSTICA:.",
    "telegrafico": "Estilo telegráfico de radiólogo con prisa, frases cortas y alguna abreviatura "
    "habitual (LSD, LII, D4-D5, etc.), con cabeceras HALLAZGOS: y CONCLUSIÓN:.",
}
CONTENT = [
    (
        "un hallazgo lateralizado (derecho o izquierdo) que se repite en la conclusión con el "
        "mismo lado"
    ),
    "una lesión con su medida en mm o cm que se repite en la conclusión con la misma medida",
    (
        "un hallazgo negado explícitamente en los hallazgos (no se observa / sin / ausencia de) "
        "que la conclusión también menciona como ausente"
    ),
    "hallazgos bilaterales o en ambos lados con estructuras distintas a cada lado",
    "una comparación con un estudio previo con medidas antes y ahora",
    "un estudio normal con varias negaciones",
]

PROMPT = """Escribe un informe radiológico ficticio en español de España, realista, de un radiólogo.
Exploración: {modality} {region}.
Estilo: {style}
Debe incluir: {content}; y además {content2}.
Extensión: unas {words} palabras.
Reglas: inventa todo (no copies casos reales), no pongas nombres, fechas ni datos del paciente,
no incluyas errores ni contradicciones, la conclusión resume y reformula los hallazgos.
Devuelve solo el texto del informe, sin comentarios ni formato markdown."""


def specs(n: int, rng: random.Random) -> list[dict]:
    out = []
    for i in range(n):
        modality = rng.choice(list(MODALITIES))
        content, content2 = rng.sample(CONTENT, 2)
        out.append(
            {
                "id": f"syn-{i:05d}",
                "modality": modality,
                "region": rng.choice(MODALITIES[modality]),
                "style": rng.choice(list(STYLES)),
                "content": content,
                "content2": content2,
                "words": rng.choice([90, 150, 220, 320]),
            }
        )
    return out


def clean_text(text: str) -> str:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"[*#`]+", "", text)  # stray markdown
    return text.strip()


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--model", default="Qwen/Qwen3.8-27B-FP8")
    ap.add_argument("--n", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--temperature", type=float, default=0.8)
    ap.add_argument("--out", default="data/synthetic/reports.jsonl")
    args = ap.parse_args()

    from vllm import LLM, SamplingParams

    rng = random.Random(args.seed)
    items = specs(args.n, rng)
    conversations = [
        [
            {
                "role": "user",
                "content": PROMPT.format(**{**it, "style": STYLES[it["style"]]}),
            }
        ]
        for it in items
    ]
    # Qwen3.5+ is hybrid (Gated DeltaNet): every running sequence needs one Mamba cache block,
    # and only ~576 fit next to a 27B model, below vLLM's default of 1,024 sequences.
    llm = LLM(
        model=args.model,
        max_model_len=4096,
        gpu_memory_utilization=0.88,
        max_num_seqs=256,
        seed=args.seed,
    )
    params = SamplingParams(temperature=args.temperature, top_p=0.95, max_tokens=1200)
    outputs = llm.chat(
        conversations, params, chat_template_kwargs={"enable_thinking": False}, use_tqdm=True
    )

    kept, seen, dropped = [], set(), {"no_sections": 0, "length": 0, "duplicate": 0}
    for it, out in zip(items, outputs):
        text = clean_text(out.outputs[0].text)
        words = len(text.split())
        digest = hashlib.sha256(re.sub(r"\W+", "", text.lower()).encode()).hexdigest()
        if split_sections(text) is None:
            dropped["no_sections"] += 1
        elif not 50 <= words <= 600:
            dropped["length"] += 1
        elif digest in seen:
            dropped["duplicate"] += 1
        else:
            seen.add(digest)
            kept.append({"id": it["id"], "text": text, "spec": it, "generator": args.model})

    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(k, ensure_ascii=False) + "\n" for k in kept)
    print(json.dumps({"requested": args.n, "kept": len(kept), "dropped": dropped}, indent=2))


if __name__ == "__main__":
    main()
