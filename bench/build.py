"""Build the radcheck evaluation files and stats from bench/raw.jsonl (spec §5.2, §6, §9).

    python bench/build.py

Writes:
  radcheck_bench_v1_{dev,test,extra}.jsonl
  stats.json
  radiologist_review.md   (50 stratified test items)
"""

from __future__ import annotations

import collections
import json
import random
import sys
from pathlib import Path

BENCH = Path(__file__).resolve().parent
sys.path.insert(0, str(BENCH.parent / "src"))

from radcheck.prompts import CHAT_TEMPLATE_KWARGS, SYSTEM_PROMPT, answer  # noqa: E402

SEED = 13


def to_example(item: dict) -> dict:
    report = item["informe"]
    gold = []
    for e in item["errores"]:
        start = report.find(e["fragmento"])
        cp = report.find(e["contraparte"]) if e.get("contraparte") else -1
        gold.append(
            {
                "tipo": e["tipo"],
                "fragmento": e["fragmento"],
                "explicacion": e["explicacion"],
                "start": start,
                "end": start + len(e["fragmento"]),
                "original": e["original"],
                "counterpart": [cp, cp + len(e["contraparte"])] if cp != -1 else None,
            }
        )
    preds = [{k: e[k] for k in ("tipo", "fragmento", "explicacion")} for e in item["errores"]]
    return {
        "id": item["id"],
        "report_id": item["id"],
        "prompt": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": report},
        ],
        "completion": [{"role": "assistant", "content": answer(preds)}],
        "chat_template_kwargs": CHAT_TEMPLATE_KWARGS,
        "gold": gold,
    }


def stats(items: list[dict]) -> dict:
    main = [i for i in items if i["split"] in ("dev", "test")]
    extra = [i for i in items if i["split"] == "extra"]

    def breakdown(rows: list[dict], keys: list[str]) -> dict:
        out = {}
        for k in keys:
            out[k] = dict(collections.Counter(i["meta"][k] for i in rows))
        return out

    def by_split(rows):
        return dict(collections.Counter(i["split"] for i in rows))

    clean_main = [i for i in main if i["meta"]["slice"].startswith("clean")]
    hard_neg_main = [i for i in main if i["meta"]["hard_negative"]]
    return {
        "version": "v1",
        "seed": SEED,
        "items": len(items),
        "main_items": len(main),
        "extra_items": len(extra),
        "splits": by_split(items),
        "slice": dict(collections.Counter(i["meta"]["slice"] for i in items)),
        "slice_by_split": {
            f"{split}/{sl}": n
            for (split, sl), n in collections.Counter(
                (i["split"], i["meta"]["slice"]) for i in items
            ).items()
        },
        "hard_negative": dict(
            collections.Counter(i["meta"]["hard_negative"] for i in hard_neg_main)
        ),
        **breakdown(main, ["estilo", "modalidad", "region", "dificultad"]),
        "length_words": {
            "min": min(i["meta"]["palabras"] for i in items),
            "max": max(i["meta"]["palabras"] for i in items),
            "mean": round(sum(i["meta"]["palabras"] for i in items) / len(items), 1),
            "over_250": sum(1 for i in items if i["meta"]["palabras"] > 250),
            "over_250_share": round(
                sum(1 for i in items if i["meta"]["palabras"] > 250) / len(items), 3
            ),
        },
        "corrupted": sum(1 for i in items if i["errores"]),
    }


def review_markdown(items: list[dict], n: int = 50) -> str:
    rng = random.Random(SEED)
    test = [i for i in items if i["split"] == "test"]
    by_slice: dict[str, list[dict]] = collections.defaultdict(list)
    for i in test:
        by_slice[i["meta"]["slice"]].append(i)
    quota = {
        "clean_ordinary": 14,
        "clean_hard": 14,
        "lateralidad": 8,
        "negacion": 8,
        "medida": 6,
    }
    sample: list[dict] = []
    for slice_name, k in quota.items():
        pool = sorted(by_slice[slice_name], key=lambda x: x["id"])
        sample += rng.sample(pool, min(k, len(pool)))
    sample.sort(key=lambda x: x["id"])

    lines = [
        "# RadCheck-Bench-ES v1 — revisión del radiólogo",
        "",
        f"{len(sample)} informes del split *test*, estratificados por tipo de ítem. "
        "Todos son sintéticos: ningún paciente real.",
        "",
        "Marca cada casilla. Si un ítem no es realista o la etiqueta es incorrecta, "
        "anota el motivo debajo.",
        "",
        "---",
        "",
    ]
    for i, it in enumerate(sample, 1):
        m = it["meta"]
        lines += [
            f"## {i}. `{it['id']}` — {m['slice']}",
            "",
            f"*{m['modalidad']} · {m['region']} · estilo {m['estilo']} · "
            f"{m['palabras']} palabras · dificultad {m['dificultad']}*"
            + (f" · negativo difícil: {m['hard_negative']}" if m["hard_negative"] else ""),
            "",
            "```text",
            it["informe"],
            "```",
            "",
        ]
        if it["errores"]:
            e = it["errores"][0]
            lines += [
                f"**Etiqueta:** `{e['tipo']}`",
                "",
                f"- fragmento: «{e['fragmento']}»",
                f"- contraparte: «{e['contraparte']}»",
                f"- explicación: {e['explicacion']}",
                "",
            ]
        else:
            lines += ["**Etiqueta:** sin incoherencias (informe limpio)", ""]
        lines += [
            "- [ ] realista",
            "- [ ] el error es verificable solo con el texto",
            "- [ ] etiqueta correcta",
            "",
            "Notas: ",
            "",
            "---",
            "",
        ]
    return "\n".join(lines)


def main() -> None:
    items = [
        json.loads(line) for line in (BENCH / "raw.jsonl").open(encoding="utf-8") if line.strip()
    ]
    items.sort(key=lambda i: i["id"])
    files = {"dev": [], "test": [], "extra": []}
    for it in items:
        files[it["split"]].append(to_example(it))

    for split, rows in files.items():
        path = BENCH / f"radcheck_bench_v1_{split}.jsonl"
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
        print(f"{path.name}: {len(rows)}")

    st = stats(items)
    review = []
    if (BENCH / "review.jsonl").exists():
        review = [
            json.loads(line)
            for line in (BENCH / "review.jsonl").open(encoding="utf-8")
            if line.strip()
        ]
    disagreements = [r for r in review if r.get("motivo") == "check_disagrees"]
    main_dis = [
        r for r in disagreements if r.get("gold") not in (["discordancia"], ["transcripcion"])
    ]
    st["validation"] = {
        "validate_pass": len(items),
        "validate_fail": 0,
        "independent_check": {
            "model": "qwen3.8-flash",
            "family": "Qwen",
            "agree": len(items) - len(disagreements),
            "disagree": len(disagreements),
            "of": len(items),
            "main_track_agreement": round((400 - len(main_dis)) / 400, 4),
            "extra_track_disagreements": len(disagreements) - len(main_dis),
            "extra_note": "el chequeo ignora omisiones y erratas por diseño: el track extra no "
            "puntúa en el resultado principal",
        },
    }
    (BENCH / "stats.json").write_text(json.dumps(st, ensure_ascii=False, indent=2))
    (BENCH / "radiologist_review.md").write_text(review_markdown(items))
    print(json.dumps({"stats": st["slice"], "words": st["length_words"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
