"""Build RadCheck-Bench-ES v1: specs, generation against DeepSeek, independent check.

Subcommands
-----------
  specs       write bench/specs.jsonl deterministically (no API calls)
  generate    clean report + corruption per spec -> bench/raw.jsonl
  check       independent verification prompt -> bench/review.jsonl
  usage       print token usage accumulated in bench/usage.json

The API key is read from DEEPSEEK_API_KEY at call time and is never written anywhere.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BENCH = Path(__file__).resolve().parent
PROMPTS = BENCH / "prompts"
sys.path.insert(0, str(BENCH))
SEED = 13
MODEL = os.environ.get("RADCHECK_BENCH_MODEL", "deepseek-v4-flash")
CHECK_MODEL = os.environ.get("RADCHECK_BENCH_CHECK_MODEL", "qwen3.8-flash")
BASE_URL = os.environ.get("RADCHECK_BENCH_BASE_URL", "https://api.deepseek.com/v1")
KEY_VAR = "DEEPSEEK_API_KEY"
CHECK_BASE_URL = os.environ.get("RADCHECK_BENCH_CHECK_BASE_URL", BASE_URL)
CHECK_KEY_VAR = os.environ.get("RADCHECK_BENCH_CHECK_KEY_VAR", KEY_VAR)
TEMPERATURE = 0.8

# ---------------------------------------------------------------- composition

N_MAIN = 400
DEV = {"clean_ordinary": 15, "clean_hard": 15, "lateralidad": 10, "negacion": 10, "medida": 10}
MAIN = {
    "clean_ordinary": 100,
    "clean_hard": 100,
    "lateralidad": 67,
    "negacion": 67,
    "medida": 66,
}
EXTRA = {"discordancia": 30, "transcripcion": 30}

HARD_NEGATIVES = [
    "laterales_distintos",
    "bilateral_asimetrico",
    "negacion_estructura_distinta",
    "mismo_numero_estructuras_distintas",
    "comparacion_previa",
    "organo_sin_lateralidad",
]

MODALITY_REGION = [
    ("RX", "tórax"),
    ("TC", "tórax"),
    ("TC", "abdomen-pelvis"),
    ("TC", "neuro"),
    ("TC", "columna"),
    ("TC", "cabeza-cuello"),
    ("RM", "neuro"),
    ("RM", "columna"),
    ("RM", "musculoesquelético"),
    ("RM", "abdomen-pelvis"),
    ("ecografía", "abdomen-pelvis"),
    ("ecografía", "musculoesquelético"),
    ("ecografía", "cabeza-cuello"),
    ("mamografía", "mama"),
]

MEASURE_VARIANTS = ["unit_swap", "x10", "digit_slip", "decimal_slip"]


def _length_target(rng: random.Random) -> tuple[int, int, str]:
    """Return (min, max, band). At least ~35% land above 250 words."""
    r = rng.random()
    if r < 0.34:
        return 60, 160, "short"
    if r < 0.66:
        return 160, 251, "medium"
    return 251, 500, "long"


def build_specs() -> list[dict]:
    rng = random.Random(SEED)

    slices: list[str] = []
    for name, n in MAIN.items():
        slices += [name] * n
    rng.shuffle(slices)

    # dev picks: DEV counts, drawn from the shuffled order so dev is not biased to one block.
    dev_quota = dict(DEV)
    split_of: dict[int, str] = {}
    for i, s in enumerate(slices):
        if dev_quota.get(s, 0) > 0:
            split_of[i] = "dev"
            dev_quota[s] -= 1
        else:
            split_of[i] = "test"
    assert not any(dev_quota.values()), dev_quota

    styles = ["A", "B", "C", "D"]
    mr_pool = MODALITY_REGION[:]
    rng.shuffle(mr_pool)

    specs: list[dict] = []
    for i, sl in enumerate(slices):
        modality, region = mr_pool[i % len(mr_pool)]
        estilo = styles[i % 4]
        lo, hi, band = _length_target(rng)
        spec: dict = {
            "id": f"rcb-{i + 1:04d}",
            "split": split_of[i],
            "slice": sl,
            "modalidad": modality,
            "region": region,
            "estilo": estilo,
            "longitud": {"min": lo, "max": hi, "banda": band},
        }
        if sl.startswith("clean"):
            spec["hard_negative"] = (
                HARD_NEGATIVES[i % len(HARD_NEGATIVES)] if sl == "clean_hard" else None
            )
            spec["dificultad"] = "easy" if sl == "clean_ordinary" else "hard"
        else:
            spec["hard_negative"] = None
            if sl == "lateralidad":
                spec["ubicacion_error"] = "conclusion" if i % 2 else "hallazgos"
                spec["direccion"] = None
                spec["variante"] = None
            elif sl == "negacion":
                spec["ubicacion_error"] = "conclusion" if i % 2 else "hallazgos"
                spec["direccion"] = "negacion_a_afirmacion" if i % 2 else "afirmacion_a_negacion"
                spec["variante"] = None
            else:
                spec["ubicacion_error"] = "conclusion" if i % 2 else "hallazgos"
                spec["direccion"] = None
                spec["variante"] = MEASURE_VARIANTS[i % len(MEASURE_VARIANTS)]
            spec["dificultad"] = ["easy", "medium", "hard"][i % 3]
        specs.append(spec)

    for j, (sl, n) in enumerate(EXTRA.items()):
        for k in range(n):
            i = len(specs)
            modality, region = mr_pool[i % len(mr_pool)]
            lo, hi, band = _length_target(rng)
            specs.append(
                {
                    "id": f"rcb-x{i + 1:04d}",
                    "split": "extra",
                    "slice": sl,
                    "modalidad": modality,
                    "region": region,
                    "estilo": styles[i % 4],
                    "longitud": {"min": lo, "max": hi, "banda": band},
                    "hard_negative": None,
                    "dificultad": ["easy", "medium", "hard"][i % 3],
                    "ubicacion_error": None,
                    "direccion": None,
                    "variante": None,
                }
            )
    return specs


PILOT = [
    # 2 clean ordinary, 2 clean hard, 2 per error type, 2 extra
    ("clean_ordinary", None, None, None),
    ("clean_ordinary", None, None, None),
    ("clean_hard", "bilateral_asimetrico", None, None),
    ("clean_hard", "comparacion_previa", None, None),
    ("lateralidad", None, None, "conclusion"),
    ("lateralidad", None, None, "hallazgos"),
    ("negacion", None, "negacion_a_afirmacion", "conclusion"),
    ("negacion", None, "afirmacion_a_negacion", "hallazgos"),
    ("medida", None, None, "conclusion"),
    ("medida", None, None, "hallazgos"),
    ("discordancia", None, None, None),
    ("transcripcion", None, None, None),
]


def cmd_specs(_: argparse.Namespace) -> None:
    specs = build_specs()
    out = BENCH / "specs.jsonl"
    out.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in specs))
    counts: dict[str, int] = {}
    for s in specs:
        counts[s["slice"]] = counts.get(s["slice"], 0) + 1
    print(json.dumps({"total": len(specs), "slices": counts}, ensure_ascii=False, indent=2))
    print(f"wrote {out}")


def cmd_pilot(args: argparse.Namespace) -> None:
    specs = [json.loads(line) for line in (BENCH / "specs.jsonl").read_text().splitlines()]
    chosen: list[dict] = []
    for sl, hn, direccion, ubic in PILOT:
        match = next(
            s
            for s in specs
            if s["slice"] == sl
            and s not in chosen
            and (hn is None or s.get("hard_negative") == hn)
            and (direccion is None or s.get("direccion") == direccion)
            and (ubic is None or s.get("ubicacion_error") == ubic)
        )
        chosen.append(match)
    run(list(chosen), args)


def cmd_generate(args: argparse.Namespace) -> None:
    specs = [json.loads(line) for line in (BENCH / "specs.jsonl").read_text().splitlines()]
    if args.ids:
        wanted = set(args.ids.split(","))
        specs = [s for s in specs if s["id"] in wanted]
    run(specs, args)


# ----------------------------------------------------------------------- API

_usage_lock = threading.Lock()


def _record_usage(kind: str, model: str, usage) -> None:
    if usage is None:
        return
    path = BENCH / "usage.json"
    with _usage_lock:
        data = json.loads(path.read_text()) if path.exists() else {}
        row = data.setdefault(model, {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0})
        row["calls"] += 1
        row["prompt_tokens"] += usage.prompt_tokens
        row["completion_tokens"] += usage.completion_tokens
        data["_last_kind"] = kind
        path.write_text(json.dumps(data, indent=2))


def _client(base_url: str | None = None, key_var: str | None = None):
    from openai import OpenAI

    var = key_var or KEY_VAR
    key = os.environ.get(var)
    if not key:
        sys.exit(f"{var} is not set")
    return OpenAI(base_url=base_url or BASE_URL, api_key=key)


def _chat(
    client,
    model: str,
    system: str,
    user: str,
    *,
    json_mode: bool = True,
    temperature: float | None = None,
    seed: int | None = None,
) -> str:
    kwargs: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": TEMPERATURE if temperature is None else temperature,
        "max_tokens": 4000,
        "seed": seed if seed is not None else SEED,
        # deepseek-v4-flash thinks by default (~70 reasoning tokens on a one-line answer).
        "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    r = client.chat.completions.create(**kwargs)
    _record_usage("chat", model, getattr(r, "usage", None))
    return r.choices[0].message.content or ""


def _template(name: str) -> str:
    return (PROMPTS / name).read_text()


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        text = text[text.find("{") :]
    return json.loads(text)


HARD_NEGATIVE_FOCO = {
    "laterales_distintos": (
        "Incluye al menos dos hallazgos distintos, cada uno con un lado distinto (por ejemplo "
        "una hernia foraminal izquierda en un nivel y otra derecha en otro nivel). Cada hallazgo "
        "debe conservar SU lado en la conclusión."
    ),
    "bilateral_asimetrico": (
        "Incluye un hallazgo bilateral con predominio claro de un lado (por ejemplo un derrame "
        "pleural bilateral, mayor en el lado derecho). Mantén esa asimetría en la conclusión."
    ),
    "negacion_estructura_distinta": (
        "Incluye una negación y una afirmación sobre estructuras anatómicas DISTINTAS (por "
        "ejemplo: no se observan adenopatías axilares; adenopatía supraclavicular de 12 mm). "
        "Ambas menciones deben repetirse coherentes en la conclusión."
    ),
    "mismo_numero_estructuras_distintas": (
        "Incluye la misma cifra aplicada a dos estructuras distintas (por ejemplo un quiste "
        "hepático de 12 mm y un nódulo tiroideo de 12 mm). No hay contradicción: son hallazgos "
        "diferentes."
    ),
    "comparacion_previa": (
        "Incluye una comparación con un estudio previo con dos cifras distintas para el mismo "
        "hallazgo, dejando claro cuál es la antigua y cuál la actual (por ejemplo: previamente "
        "15 mm, actualmente 18 mm). Menciona también esa evolución en la conclusión."
    ),
    "organo_sin_lateralidad": (
        "Incluye órganos sin lateralidad (íleon, bazo, aorta, útero, páncreas) junto a palabras "
        "de lado usadas correctamente para otras estructuras cercanas."
    ),
}


def _foco(spec: dict) -> str:
    if spec["slice"] == "clean_hard":
        pattern = spec["hard_negative"]
        return (
            "Requisito adicional para este informe: "
            + HARD_NEGATIVE_FOCO[pattern]
            + " Este informe NO debe contener ninguna contradicción interna."
        )
    if spec["slice"] == "clean_ordinary":
        return (
            "Requisito adicional para este informe: incluye dos hallazgos que se mencionen "
            "en los hallazgos y otra vez en la conclusión, con la misma lateralidad, el mismo "
            "sentido (afirmado o negado) y la misma cifra en ambos sitios."
        )
    tipo = spec["slice"]
    return (
        f"Requisito adicional para este informe: usa {tipo} en un hallazgo concreto y vuelve "
        "a mencionarlo en la conclusión reformulándolo (otra frase, otro orden), de modo que "
        "el hallazgo quede descrito dos veces con la misma lateralidad, el mismo sentido y la "
        "misma cifra. No lo menciones una tercera vez."
    )


def _clean_prompt(spec: dict) -> str:
    return _template("clean_report.txt").format(
        modalidad=spec["modalidad"],
        region=spec["region"],
        estilo=spec["estilo"],
        min=spec["longitud"]["min"],
        max=spec["longitud"]["max"],
        dificultad=spec["dificultad"],
        foco=_foco(spec),
        slice=spec["slice"],
        hard_negative=spec.get("hard_negative") or "-",
        ubicacion=spec.get("ubicacion_error") or "-",
        direccion=spec.get("direccion") or "-",
        variante=spec.get("variante") or "-",
    )


def _corrupt_prompt(spec: dict, report: str) -> str:
    if spec["slice"] in ("discordancia", "transcripcion"):
        return _template(f"corrupt_{spec['slice']}.txt").format(informe=report)
    return _template("corrupt.txt").format(
        slice=spec["slice"],
        ubicacion=spec.get("ubicacion_error") or "-",
        direccion=spec.get("direccion") or "-",
        variante=spec.get("variante") or "-",
        dificultad=spec["dificultad"],
        informe=report,
    )


WORD = __import__("re").compile(r"\S+")
SENT_END = ".!?;\n"
STOP = {
    "de",
    "del",
    "la",
    "el",
    "los",
    "las",
    "un",
    "una",
    "en",
    "con",
    "y",
    "o",
    "a",
    "al",
    "por",
    "para",
    "que",
    "se",
    "su",
    "sus",
    "sin",
    "sobre",
}


def _pick_occurrence(report: str, old: str, counterpart: str) -> int | None:
    """Where to apply the edit: the single occurrence not overlapping `counterpart`.

    A repeated word ("masa", "lesión") is most often repeated *because* the conclusion
    restates the finding, so the mention inside the counterpart is the one to preserve.
    """
    hits = [m.start() for m in __import__("re").finditer(__import__("re").escape(old), report)]
    if len(hits) == 1:
        return hits[0]
    if not counterpart:
        return None
    cp_spans = [
        (m.start(), m.end())
        for m in __import__("re").finditer(__import__("re").escape(counterpart), report)
    ]
    free = [h for h in hits if not any(s - len(old) < h < e for s, e in cp_spans)]
    return free[0] if len(free) == 1 else None


def _window(
    text: str, start: int, length: int, target: int = 8, lo_w: int = 3, hi_w: int = 12
) -> str:
    """A 3-12 word window around [start, start+length), sliced from `text` verbatim.

    Slicing by word offsets keeps commas and brackets intact, so the result is always an
    exact substring and never widens past a sentence boundary unless the sentence is too
    short to reach `lo_w` words.
    """
    if start < 0:
        return ""
    spans = [(m.start(), m.end()) for m in WORD.finditer(text)]
    edit_lo, edit_hi = start, start + max(length, 0)
    if edit_hi == edit_lo:
        # Pure deletion: the cut point usually falls on whitespace, so anchor on the word
        # that now follows it (or the last word that preceded it).
        # Anchor forward: the fragment then lies wholly inside the following sentence, so it
        # never straddles the boundary the deletion created.
        nxt = [
            i
            for i, (a, b) in enumerate(spans)
            if a >= edit_lo and any(c.isalnum() for c in text[a:b])
        ]
        prev = [
            i
            for i, (a, b) in enumerate(spans)
            if b <= edit_lo and any(c.isalnum() for c in text[a:b])
        ]
        k = nxt[0] if nxt else (prev[-1] if prev else -1)
        if k < 0:
            return ""
        edit_lo, edit_hi = spans[k]
    else:
        k = next(
            (i for i, (a, b) in enumerate(spans) if a < edit_hi and edit_lo < b),
            None,
        )
    if k is None:
        return ""

    def sentence_bounds(idx: int) -> tuple[int, int]:
        a = max((text.rfind(c, 0, spans[idx][0]) for c in SENT_END), default=-1) + 1
        ends = [text.find(c, spans[idx][1]) for c in SENT_END]
        ends = [e for e in ends if e != -1]
        b = min(ends) if ends else len(text)
        i = next(i for i, (s, _) in enumerate(spans) if s >= a)
        j = max(i for i, (_, e) in enumerate(spans) if e <= b + 1)
        return i, j

    i, j = sentence_bounds(k)
    sentence_words = j - i + 1
    width = max(lo_w, min(target, hi_w, sentence_words))
    while width < lo_w:  # sentence too short: absorb neighbours
        if i > 0:
            i -= 1
            width += 1
        elif j < len(spans) - 1:
            j += 1
            width += 1
        else:
            break
    while j - i + 1 > width:  # shrink around the edit
        left, right = k - i, j - k
        if left > right and i < k:
            i += 1
        elif j > k:
            j -= 1
        elif i < k:
            i += 1
        else:
            break
    # Trim edge function words so the fragment starts and ends on content.
    # Never trim across the edited word: the fragment must contain the change.
    while (
        j - i + 1 > lo_w
        and spans[i][1] <= edit_lo
        and text[spans[i][0] : spans[i][1]].lower().strip(",;:.") in STOP
    ):
        i += 1
    while (
        j - i + 1 > lo_w
        and spans[j][0] >= edit_hi
        and text[spans[j][0] : spans[j][1]].lower().strip(",;:.") in STOP
    ):
        j -= 1
    frag = text[spans[i][0] : spans[j][1]].rstrip(" ,;:")
    return frag if frag in text else text[spans[i][0] : spans[j][1]]


def _validate(item: dict, spec: dict) -> list[str]:
    """Same rules as bench/validate.py, so generation never emits an item that will fail."""
    from validate import check_item

    return check_item(item, spec)


_SEEN_TEXTS: dict[str, str] = {}
_SEEN_LOCK = threading.Lock()


def _claim_text(text: str, spec_id: str) -> bool:
    """Reserve a normalised report text so no two items share the same base report."""
    from validate import norm

    key = norm(text)
    with _SEEN_LOCK:
        owner = _SEEN_TEXTS.get(key)
        if owner is None or owner == spec_id:
            _SEEN_TEXTS[key] = spec_id
            return True
        return False


def _one_retry(spec: dict, client, model: str, attempts: int = 6) -> dict | None:
    """Generation is stochastic; a rejected edit is retried, never silently dropped."""
    for n in range(attempts):
        item = _one(spec, client, model, temperature=0.75 + 0.05 * n, attempt=n)
        if item is None:
            print(f"[retry] {spec['id']} attempt {n + 1}/{attempts}", file=sys.stderr)
            continue
        problems = _validate(item, spec)
        if not problems and not _claim_text(item["informe"], spec["id"]):
            problems = ["duplicate_report"]
        if not problems:
            return item
        print(f"[retry] {spec['id']} attempt {n + 1}/{attempts}: {problems}", file=sys.stderr)
    return None


def _seed_for(spec_id: str, attempt: int = 0) -> int:
    """Per-item seed. A global seed plus an identical prompt makes the gateway replay the
    same report, which produced duplicate items across specs with the same ficha."""
    import zlib

    return SEED + zlib.crc32(spec_id.encode()) % 100_000 + attempt * 7919


def _one(spec: dict, client, model: str, temperature: float | None = None,
         attempt: int = 0) -> dict | None:
    clean = _parse_json(
        _chat(
            client,
            model,
            _template("generator_system.txt"),
            _clean_prompt(spec),
            temperature=temperature,
        )
    )
    report = (clean.get("informe_limpio") or "").strip()
    if not report:
        print(f"[warn] {spec['id']}: empty report", file=sys.stderr)
        return None
    report = __import__("re").sub(r"[ \t]{2,}", " ", report)

    errores: list[dict] = []
    informe = report
    if spec["slice"] not in ("clean_ordinary", "clean_hard"):
        raw = _chat(
            client,
            model,
            _template("generator_system.txt"),
            _corrupt_prompt(spec, report),
            temperature=temperature,
        )
        edit = _parse_json(raw)
        old = (edit.get("original") or "").strip()
        new = (edit.get("nuevo") or "").strip()
        cp = (edit.get("contraparte") or "").strip()
        deletion_ok = spec["slice"] == "discordancia"
        if not old or (new == "" and not deletion_ok) or old == new:
            print(f"[warn] {spec['id']}: bad edit {edit}", file=sys.stderr)
            return None
        at = _pick_occurrence(report, old, cp)
        if at is None:
            print(f"[warn] {spec['id']}: cannot disambiguate {old!r}", file=sys.stderr)
            return None
        informe = report.replace(old, new, 1)
        if new == "":
            # Deleting a clause leaves " ." behind; the stray space is part of the edit.
            informe = __import__("re").sub(r"[ \t]+([.,;:])", r"\1", informe)
            informe = __import__("re").sub(r"[ \t]{2,}", " ", informe)
        # The fragment is DERIVED, never copied from the model: the whole sentence-level
        # window around the edit, taken from the corrupted text so it stays an exact substring.
        frag = _window(informe, at, len(new))
        if not frag:
            print(f"[warn] {spec['id']}: no window", file=sys.stderr)
            return None
        if spec["slice"] == "transcripcion" and len(new.split()) != 1:
            print(f"[warn] {spec['id']}: transcription edit is not one word", file=sys.stderr)
            return None
        errores = [
            {
                "tipo": spec["slice"],
                "fragmento": frag,
                "contraparte": cp,
                "explicacion": (edit.get("explicacion") or "").strip(),
                "original": old,
            }
        ]

    return {
        "id": spec["id"],
        "split": spec["split"],
        "informe_limpio": report,
        "informe": informe,
        "errores": errores,
        "meta": {
            "modalidad": spec["modalidad"],
            "region": spec["region"],
            "estilo": spec["estilo"],
            "dificultad": spec["dificultad"],
            "hard_negative": spec.get("hard_negative"),
            "palabras": len(report.split()),
            "generador": model,
            "slice": spec["slice"],
        },
    }


def run(specs: list[dict], args: argparse.Namespace) -> None:
    client = _client()
    out = BENCH / "raw.jsonl"
    done = set()
    if out.exists() and not args.force:
        done = {json.loads(line)["id"] for line in out.read_text().splitlines() if line.strip()}
    if out.exists():
        for line in out.read_text().splitlines():
            if line.strip():
                prev = json.loads(line)
                _claim_text(prev["informe"], prev["id"])
    todo = [s for s in specs if s["id"] not in done]
    print(f"{len(todo)} specs to generate with {MODEL}", file=sys.stderr)

    lock = threading.Lock()

    def work(spec: dict) -> dict | None:
        # Transport/validation errors are transient (the gateway occasionally routes to an
        # unserved "-fallback" model), so retry before giving up on an id.
        for attempt in range(5):
            try:
                return _one_retry(spec, client, MODEL)
            except Exception as exc:  # noqa: BLE001 - keep going, report the id
                print(f"[error] {spec['id']} try {attempt + 1}/5: {exc}", file=sys.stderr)
                time.sleep(2 * (attempt + 1))
        return None

    with ThreadPoolExecutor(max_workers=args.workers) as pool, out.open("a", encoding="utf-8") as f:
        for item in pool.map(work, todo):
            if item is None:
                continue
            with lock:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                f.flush()
    print(f"wrote {out}")


def cmd_check(args: argparse.Namespace) -> None:
    """Independent pass: only `informe`, a different prompt, a different model family."""
    client = _client(CHECK_BASE_URL, CHECK_KEY_VAR)
    items = [json.loads(line) for line in (BENCH / "raw.jsonl").read_text().splitlines()]
    if args.ids:
        wanted = set(args.ids.split(","))
        items = [it for it in items if it["id"] in wanted]
    system = _template("checker_system.txt")
    review_path = BENCH / "review.jsonl"
    ok, bad = 0, 0
    with review_path.open("w", encoding="utf-8") as rev:
        for it in items:
            user = _template("checker_user.txt").format(informe=it["informe"])
            try:
                found = _parse_json(_chat(client, CHECK_MODEL, system, user))
            except Exception as exc:  # noqa: BLE001
                rev.write(
                    json.dumps(
                        {"id": it["id"], "motivo": "check_failed", "detalle": str(exc)},
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                bad += 1
                continue
            errs = found.get("incoherencias") or []
            gold = {e["tipo"] for e in it["errores"]}
            pred = {e.get("tipo") for e in errs if isinstance(e, dict)}
            if (gold == pred) or (not gold and not pred):
                ok += 1
            else:
                bad += 1
                rev.write(
                    json.dumps(
                        {
                            "id": it["id"],
                            "motivo": "check_disagrees",
                            "gold": sorted(gold),
                            "checker": errs,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
    print(json.dumps({"agree": ok, "disagree": bad, "of": len(items)}))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("specs").set_defaults(fn=cmd_specs)
    for name, fn in (("pilot", cmd_pilot), ("generate", cmd_generate)):
        p = sub.add_parser(name)
        p.add_argument("--workers", type=int, default=4)
        p.add_argument("--force", action="store_true")
        if name == "generate":
            p.add_argument("--ids", help="comma-separated spec ids")
        p.set_defaults(fn=fn)
    pc = sub.add_parser("check")
    pc.add_argument("--ids", help="comma-separated ids")
    pc.set_defaults(fn=cmd_check)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
