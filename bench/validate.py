"""Validate bench/raw.jsonl against the RadCheck-Bench-ES v1 rules (spec §4, §5, §7.4).

Every kept item must pass; failures are reported with a machine-readable reason code.

    python bench/validate.py            # validate raw.jsonl, print report
    python bench/validate.py --ids a,b  # only these ids
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import unicodedata
from pathlib import Path

BENCH = Path(__file__).resolve().parent
MIN_WORDS, MAX_WORDS = 60, 500
STYLE_MARKERS = {
    "A": [r"\bEXPLORACI[ÓO]N\b", r"\bHALLAZGOS\b", r"\bCONCLUSI[ÓO]N\b"],
    "B": [],
    "C": [r"\bIMPRESI[ÓO]N\b"],
    "D": [],
}
ABBREV = re.compile(r"\b(dcho|izq|lsd|lii|lad|lai|d4|l4|t12|c7|ap|pa|rc|sos|sn|mm|cm)\b", re.I)
SIDE = re.compile(r"\b(derech[oa]s?|izquierd[oa]s?|dcho|dcha|izq|izda|bilateral(?:es)?)\b", re.I)
NUM = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:mm|cm|m)\b", re.I)


def side_tokens(text: str) -> set[str]:
    """Normalise every side word to der/izq/bil so `dcho` and `derecho` compare equal."""
    out = set()
    for m in SIDE.finditer(text):
        w = m.group(0).lower()
        out.add("bil" if w.startswith("bilat") else "der" if w[0] == "d" else "izq")
    return out


def measure_list(text: str) -> list[str]:
    return [re.sub(r"\s+", "", m.group(0).lower()) for m in NUM.finditer(text)]


def measures(text: str) -> set[str]:
    return set(measure_list(text))


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", text).strip()


def diff_span(a: str, b: str) -> tuple[int, int, int, int]:
    """Minimal changed region between a and b: (a_start, a_end, b_start, b_end)."""
    p = 0
    while p < min(len(a), len(b)) and a[p] == b[p]:
        p += 1
    s = 0
    while s < min(len(a), len(b)) - p and a[-1 - s] == b[-1 - s]:
        s += 1
    return p, len(a) - s, p, len(b) - s


BILATERAL = re.compile(r"\bbilateral(?:es)?\b", re.I)
COMPARISON = re.compile(
    r"\b(previo|previa|previamente|anterior(?:es)?|respecto|evoluci[óo]n)\b", re.I
)
UNLATERAL_ORGANS = re.compile(r"\b(íleon|ileon|bazo|aorta|útero|utero|páncreas|pancreas)\b", re.I)
NEGATION = re.compile(r"\b(no|sin|ausencia|nunca)\b", re.I)


def hard_negative_ok(pattern: str, text: str) -> bool:
    """Evidence that the report actually instantiates the hard-negative pattern it claims."""
    sides = side_tokens(text)
    nums = measures(text)
    if pattern == "bilateral_asimetrico":
        sides = side_tokens(text)
        asym = __import__("re").search(
            r"\b(mayor|predominio|más acentuad|asimetr|mayor en)\w*", text, re.I
        )
        return bool(BILATERAL.search(text)) or (len(sides) >= 2 and bool(asym))
    if pattern == "comparacion_previa":
        return bool(COMPARISON.search(text)) and len(nums) >= 2
    if pattern == "laterales_distintos":
        return {"der", "izq"} <= sides
    if pattern == "negacion_estructura_distinta":
        return bool(NEGATION.search(text)) and bool(side_tokens(text) or nums)
    if pattern == "mismo_numero_estructuras_distintas":
        # The same number must appear twice: compare the list against its deduplicated set.
        listed = measure_list(text)
        return len(listed) != len(set(listed))
    if pattern == "organo_sin_lateralidad":
        return bool(UNLATERAL_ORGANS.search(text))
    return False


def _digits(measure: str) -> str:
    return re.sub(r"[^0-9]", "", measure)


def _related_measures(a: str, b: str) -> bool:
    """True when two measurements can be the same measurement after a plausible slip:
    unit swap (9 mm / 9 cm), x10 (9 mm / 90 mm), digit slip (19 / 9), decimal slip (1,5 / 15).
    """
    da, db = _digits(a), _digits(b)
    if not da or not db:
        return False
    if da == db:
        return True
    if len(da) == len(db):
        return sum(x != y for x, y in zip(da, db)) <= 1
    long, short = (da, db) if len(da) > len(db) else (db, da)
    if len(long) - len(short) != 1:
        return False
    return any(long[:i] + long[i + 1 :] == short or long[i] == "0" for i in range(len(long)))


NO_CONTRAST = re.compile(r"\b(sin contraste(?: iv| intravenoso)?|sin civ|no administrado)\b", re.I)
CONTRAST_USE = re.compile(
    r"\b(realce|captaci[óo]n|poscontraste|tras (?:la )?administraci[óo]n de contraste|"
    r"opacifica(?:ci[óo]n)?)\b",
    re.I,
)


def self_contradiction(text: str) -> bool:
    """A report that says "sin contraste" and then describes post-contrast behaviour
    contradicts itself, which would make a "clean" item unusable as a hard negative."""
    if not NO_CONTRAST.search(text):
        return False
    for m in CONTRAST_USE.finditer(text):
        window = text[max(0, m.start() - 80) : m.end() + 40].lower()
        # Only a POSITIVE enhancement claim contradicts "sin contraste":
        # "sin realce tras contraste" is a negation and reads fine.
        if NEGATION.search(window[: 80]):
            continue
        return True
    return False


def check_item(item: dict, spec: dict) -> list[str]:
    why: list[str] = []
    clean, corr = item["informe_limpio"], item["informe"]
    errs = item["errores"]
    words = len(corr.split())

    if not (MIN_WORDS <= words <= MAX_WORDS):
        why.append("length_out_of_range")
    # The spec's own length band is part of the ficha (§4 requires >=20% over 250 words).
    if words < spec["longitud"]["min"] or words > spec["longitud"]["max"]:
        why.append("length_outside_spec_band")
    # A generator that runs out of budget emits "…" and stops mid-sentence.
    if "…" in corr or "..." in corr:
        why.append("truncated_report")
    if not corr.rstrip().endswith((".", "!", "?")):
        why.append("unterminated_report")
    if "  " in corr:
        why.append("double_space")
    if self_contradiction(corr):
        why.append("contrast_self_contradiction")

    style = item["meta"]["estilo"]
    if style == "A":
        hits = sum(bool(re.search(m, corr)) for m in STYLE_MARKERS["A"])
        if hits < 2:
            why.append("style_marker_missing")
    elif style == "B":
        if corr.count("\n") < 2:
            why.append("style_marker_missing")
    elif style == "C":
        if not re.search(STYLE_MARKERS["C"][0], corr):
            why.append("style_marker_missing")
    elif style == "D":
        if len(ABBREV.findall(corr)) < 2:
            why.append("style_marker_missing")

    if spec["slice"].startswith("clean"):
        if clean != corr:
            why.append("clean_texts_differ")
        if errs:
            why.append("clean_has_errors")
        if spec["slice"] == "clean_hard":
            hn = item["meta"]["hard_negative"]
            if not hn:
                why.append("hard_negative_unlabelled")
            elif not hard_negative_ok(hn, corr):
                why.append("hard_negative_pattern_absent")
        return why

    if len(errs) != 1:
        why.append("error_count")
        return why

    err = errs[0]
    frag, cp = err["fragmento"], err["contraparte"]
    if err["tipo"] != spec["slice"]:
        why.append("tipo_mismatch")

    if not frag or frag not in corr:
        why.append("fragment_not_exact")
        return why
    if not cp or cp not in corr:
        why.append("counterpart_not_exact")
    if not err.get("original") or err["original"] not in clean:
        why.append("original_not_in_clean")
    if not err.get("explicacion", "").strip():
        why.append("no_explicacion")

    start = corr.find(frag)
    end = start + len(frag)

    # The two reports may differ ONLY inside the fragment span. Rather than comparing diff
    # coordinates (which live in two different strings), decompose: everything before and
    # after the fragment must be byte-identical, so `clean` = prefix + X + suffix exactly.
    prefix, suffix = corr[:start], corr[end:]
    if not clean.startswith(prefix) or not clean.endswith(suffix):
        why.append("diff_outside_fragment")
    elif len(prefix) + len(suffix) > len(clean):
        why.append("diff_outside_fragment")
    else:
        changed_clean = (
            clean[len(prefix) : len(clean) - len(suffix)] if suffix else clean[len(prefix) :]
        )
        # `frag` is the whole sentence window; isolate the words that actually differ.
        fa, fb = frag.split(), changed_clean.split()
        pre = 0
        while pre < min(len(fa), len(fb)) and fa[pre] == fb[pre]:
            pre += 1
        suf = 0
        while suf < min(len(fa), len(fb)) - pre and fa[-1 - suf] == fb[-1 - suf]:
            suf += 1
        ta = fa[pre : len(fa) - suf]
        tb = fb[pre : len(fb) - suf]
        if max(len(ta), len(tb)) > 4 and spec["slice"] != "discordancia":
            why.append("change_too_large")
        if not ta and not tb:
            why.append("no_change")

    if cp:
        for m in re.finditer(re.escape(cp), corr):
            if m.start() < end and start < m.end():
                why.append("counterpart_overlaps_fragment")
                break

    if not (3 <= len(frag.split()) <= 12):
        why.append("fragment_word_count")
    if cp and not (3 <= len(cp.split()) <= 12):
        why.append("counterpart_word_count")

    # Verifiability: the side word (or the number) must appear in both mentions.
    if err["tipo"] == "lateralidad":
        sides_f, sides_c = side_tokens(frag), side_tokens(cp)
        if not sides_f or not sides_c:
            why.append("lateralidad_without_sides")
        elif sides_f == sides_c:
            why.append("lateralidad_not_contradictory")
        if {"der", "izq"} <= sides_f:
            why.append("fragment_mentions_both_sides")
    if err["tipo"] == "medida":
        mf, mc = measures(frag), measures(cp)
        if not mf or not mc:
            why.append("medida_without_numbers")
        elif mf == mc:
            why.append("medida_identical_numbers")
        elif not any(_related_measures(a, b) for a in mf for b in mc):
            # A number that has nothing to do with the edited one is a false counterpart.
            why.append("medida_unrelated_numbers")
    if err["tipo"] == "negacion":
        neg = re.compile(r"\b(no|sin|ausencia)\b", re.I)
        if bool(neg.search(frag)) == bool(neg.search(cp)):
            why.append("negacion_not_opposed")
    # Judge the whole sentence: the clause that makes "ni" grammatical may sit outside the
    # 3-12 word fragment window.
    lo = max((corr.rfind(c, 0, start) for c in ".!?;\n"), default=-1) + 1
    ends = [corr.find(c, end) for c in ".!?;\n"]
    ends = [e for e in ends if e != -1]
    sentence = corr[lo : min(ends) if ends else len(corr)]
    if " ni " in sentence.lower():
        head = sentence[: sentence.lower().find(" ni ")]
        if not NEGATION.search(head):
            why.append("dangling_ni")
    if err["tipo"] == "transcripcion":
        if err["original"].lower() not in cp.lower():
            why.append("transcripcion_correct_form_missing")
    return why


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--raw", default=str(BENCH / "raw.jsonl"))
    ap.add_argument("--specs", default=str(BENCH / "specs.jsonl"))
    ap.add_argument("--ids", help="comma-separated ids to validate")
    ap.add_argument("--json-out", default=str(BENCH / "validation.json"))
    args = ap.parse_args()

    specs = {s["id"]: s for s in map(json.loads, Path(args.specs).open(encoding="utf-8"))}
    items = [json.loads(line) for line in Path(args.raw).open(encoding="utf-8") if line.strip()]
    if args.ids:
        wanted = set(args.ids.split(","))
        items = [it for it in items if it["id"] in wanted]

    seen: dict[str, str] = {}
    report = []
    for it in items:
        spec = specs.get(it["id"])
        why = ["unknown_spec"] if spec is None else check_item(it, spec)
        key = norm(it["informe"])
        if key in seen:
            why.append("duplicate")
        else:
            seen[key] = it["id"]
        report.append({"id": it["id"], "slice": it["meta"]["slice"], "ok": not why, "why": why})

    bad = [r for r in report if not r["ok"]]
    counts = collections.Counter(c for r in bad for c in r["why"])
    print(
        json.dumps(
            {
                "items": len(report),
                "pass": len(report) - len(bad),
                "fail": len(bad),
                "reasons": dict(counts),
                "failed_ids": [r["id"] for r in bad],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    Path(args.json_out).write_text(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
