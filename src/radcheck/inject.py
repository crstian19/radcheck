"""Rule-based error injection for Spanish radiology reports.

Design rule: an error is only injected when it creates an inconsistency that can be
verified from the text itself, i.e. between the findings and the conclusion. Swapping
"derecho" for "izquierdo" in a report that mentions the side once is undetectable even
for a radiologist, and training on it would teach the model to guess.
"""

from __future__ import annotations

import random
import re
import unicodedata
from dataclasses import dataclass, replace

ERROR_TYPES = ("lateralidad", "negacion", "medida")
# Recipe v3 adds two types that are not contradictions between two mentions:
# - discordancia: a finding described in HALLAZGOS that the conclusion no longer mentions.
# - transcripcion: a speech-recognition slip that turns a word into a non-word.
EXTENDED_TYPES = ("discordancia", "transcripcion")
ALL_ERROR_TYPES = ERROR_TYPES + EXTENDED_TYPES

# Section headers as they appear in CARES (uppercase, sometimes without accents).
_CONCLUSION_RE = re.compile(
    r"\b(?:CONCLUSI[OÓ]N(?:ES)?|IMPRESI[OÓ]N(?: DIAGN[OÓ]STICA)?|JUICIO DIAGN[OÓ]STICO)\b\s*[:.]?"
    r"|\bConclusi[oó]n(?:es)?\s*:"
)
_FINDINGS_RE = re.compile(r"\bHALLAZGOS\b\s*[:.]?")

_SIDE_RE = re.compile(r"\b(derech|izquierd)(o|a|os|as)\b", re.IGNORECASE)
_OTHER_SIDE = {"derech": "izquierd", "izquierd": "derech"}

# (pattern, kind). Group "neg" is the span removed or replaced to flip the statement.
_NEGATIONS = [
    re.compile(
        r"\b(?P<neg>[Nn]o )se (?:observa|aprecia|objetiva|identifica|visualiza|evidencia|"
        r"detecta|demuestra)n?\b"
    ),
    re.compile(
        r"\b(?P<neg>[Nn]o )(?:apreciamos|observamos|visualizamos|identificamos|objetivamos|"
        r"evidenciamos|hay|existe|existen|presenta|presentan|muestra|muestran)\b"
    ),
    # "sin X" with any noun, except fixed phrases where "con" would not be the opposite.
    re.compile(
        r"\b(?P<neg>[Ss]in) (?!embargo\b|contraste\b|otros\b|otras\b|[a-z]+(?:ar|er|ir)\b)[a-záéíóúñ]{4,}"
    ),
    re.compile(r"\b(?P<neg>[Aa]usencia) de\b"),
]
# The opposite direction: an affirmed finding that gets negated ("Se observa" -> "No se observa").
_AFFIRMATION_RE = re.compile(
    r"(?<![Nn]o )\b(?P<aff>[Ss]e) (?:observa|aprecia|objetiva|identifica|visualiza|evidencia|"
    r"detecta)n?\b"
)
_NEGATION_REPLACEMENT = {"sin": "con", "ausencia": "presencia"}

_MEASURE_RE = re.compile(r"(?<![\d.,])(?P<num>\d+(?:[.,]\d+)?)(?P<sep>\s*)(?P<unit>mm|cm)\b")

_STOPWORDS = {
    "aunque",
    "algunos",
    "algunas",
    "ambos",
    "ambas",
    "nivel",
    "parte",
    "porción",
    "porcion",
    "tamaño",
    "tamano",
    "aspecto",
    "relacion",
    "relación",
    "probable",
    "presencia",
    "signos",
    "significativa",
    "significativo",
    "normal",
    "normales",
    "previo",
    "previa",
    "estudio",
}


@dataclass(frozen=True)
class Sections:
    findings: tuple[int, int]
    conclusion: tuple[int, int]


@dataclass(frozen=True)
class Candidate:
    tipo: str
    start: int
    end: int
    replacement: str
    explicacion: str
    # The mention in the other section that the change now contradicts. From the text
    # alone either side of the contradiction may be "the error", so both count as a hit.
    counterpart: tuple[int, int] | None = None
    # discordancia removes text from the conclusion but the error is reported at the
    # finding that lost its mention, which lies elsewhere.
    report_at: tuple[int, int] | None = None


@dataclass(frozen=True)
class InjectedError:
    tipo: str
    start: int  # span of the changed text in the corrupted report
    end: int
    original: str
    fragmento: str
    explicacion: str
    counterpart: tuple[int, int] | None = None  # span in the corrupted report


def _fold(s: str) -> str:
    """Lowercase and strip accents, for fuzzy comparisons."""
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def split_sections(text: str) -> Sections | None:
    """Locate findings and conclusion. Returns None if the report lacks either."""
    concl = None
    for concl in _CONCLUSION_RE.finditer(text):
        pass
    if concl is None:
        return None
    findings_start = 0
    for m in _FINDINGS_RE.finditer(text, 0, concl.start()):
        findings_start = m.end()
    findings = (findings_start, concl.start())
    conclusion = (concl.end(), len(text))
    if findings[1] - findings[0] < 20 or conclusion[1] - conclusion[0] < 10:
        return None
    return Sections(findings=findings, conclusion=conclusion)


def _match_case(template: str, word: str) -> str:
    if template.isupper():
        return word.upper()
    if template[:1].isupper():
        return word[:1].upper() + word[1:]
    return word


def _sentence_spans(text: str, span: tuple[int, int]) -> list[tuple[int, int]]:
    return [
        (span[0] + m.start(), span[0] + m.end())
        for m in re.finditer(r"[^.\s][^.]*\.?", text[span[0] : span[1]])
    ]


def _content_words(s: str) -> set[str]:
    """Stems (first 6 letters) of the content words: "adenopatía" matches "adenopatías"."""
    return {w[:6] for w in re.findall(r"[a-zñ]{6,}", _fold(s)) if w not in _STOPWORDS}


def _is_negated(sentence: str) -> bool:
    return any(p.search(sentence) for p in _NEGATIONS)


_SCOPE_WORDS = 6  # a negation cue covers roughly the next few words ("sin X ni Y")
_GENERIC_STEMS = {"hallaz", "cambio", "especi", "respec", "valora", "previa", "previo"}


def _scope(text: str, end: int, limit: int) -> set[str]:
    """Content stems in the few words after position `end`, up to the end of the sentence."""
    stop = text.find(".", end, limit)
    words = text[end : stop if stop != -1 else limit].split()[:_SCOPE_WORDS]
    return _content_words(" ".join(words)) - _GENERIC_STEMS


def _negated_scope(sentence: str) -> set[str]:
    """Stems that a negated sentence actually denies (those right after each cue)."""
    out: set[str] = set()
    for p in _NEGATIONS:
        for m in p.finditer(sentence):
            out |= _scope(sentence, m.end("neg"), len(sentence))
    return out


def _lateral_candidates(text: str, sec: Sections) -> list[Candidate]:
    out = []
    for target, other in ((sec.conclusion, sec.findings), (sec.findings, sec.conclusion)):
        other_text = _fold(text[other[0] : other[1]])
        same_length = len(other_text) == other[1] - other[0]  # offsets valid after folding
        for m in _SIDE_RE.finditer(text, *target):
            prev = re.findall(
                r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{4,}", text[max(target[0], m.start() - 40) : m.start()]
            )
            if not prev:
                continue
            anchor = _fold(prev[-1])
            stem = _fold(m.group(1))
            # Same structure, same side, in the other section: "riñón ... izquierdo".
            cm = re.search(rf"\b{re.escape(anchor)}\b[^.]{{0,40}}?\b{stem}[a-z]*", other_text)
            if not cm:
                continue
            counterpart = (other[0] + cm.start(), other[0] + cm.end()) if same_length else None
            new_stem = _OTHER_SIDE[stem]
            new = _match_case(m.group(1), new_stem) + m.group(2)
            old_side, new_side = stem + "o", new_stem + "o"
            if target == sec.conclusion:
                why = f"La conclusión sitúa el hallazgo en el lado {new_side}, pero los hallazgos lo describen en el lado {old_side}."
            else:
                why = f"Los hallazgos describen el lado {new_side}, pero la conclusión habla del lado {old_side}."
            out.append(Candidate("lateralidad", m.start(), m.end(), new, why, counterpart))
    return out


def _negation_candidates(text: str, sec: Sections) -> list[Candidate]:
    out, seen = [], set()
    for target, other in ((sec.conclusion, sec.findings), (sec.findings, sec.conclusion)):
        other_sentences = []
        for s, e in _sentence_spans(text, other):
            negated = _is_negated(text[s:e])
            words = _negated_scope(text[s:e]) if negated else _content_words(text[s:e])
            other_sentences.append((words, (s, e), negated))
        where = "los hallazgos" if target == sec.conclusion else "la conclusión"
        plural = "n" if where == "los hallazgos" else ""

        def counterpart_for(
            m: re.Match, negated: bool, target=target, other_sentences=other_sentences
        ) -> tuple[int, int] | None:
            words = _scope(text, m.end(), target[1])
            if not words:
                return None
            return next(
                (sp for ws, sp, neg in other_sentences if neg == negated and words & ws), None
            )

        # Negation -> assertion: the other section denies the same thing.
        for pattern in _NEGATIONS:
            for m in pattern.finditer(text, *target):
                counterpart = counterpart_for(m, negated=True)
                if counterpart is None or m.start("neg") in seen:
                    continue
                seen.add(m.start("neg"))
                neg = m.group("neg")
                start, end = m.start("neg"), m.end("neg")
                if neg.strip().lower() in _NEGATION_REPLACEMENT:
                    replacement = _match_case(neg, _NEGATION_REPLACEMENT[neg.strip().lower()])
                else:
                    # "No se observan" -> "Se observan": drop "no " and keep sentence case.
                    replacement = ""
                    nxt = text[end : end + 1]
                    if neg[0].isupper() and nxt:
                        end += 1
                        replacement = nxt.upper()
                why = f"Afirma algo que {where} niega{plural}."
                out.append(Candidate("negacion", start, end, replacement, why, counterpart))

        # Assertion -> negation: the other section affirms the same thing.
        for m in _AFFIRMATION_RE.finditer(text, *target):
            counterpart = counterpart_for(m, negated=False)
            if counterpart is None:
                continue
            aff = m.group("aff")
            replacement = ("No s" if aff[0].isupper() else "no s") + aff[1:]
            why = f"Niega algo que {where} afirma{plural}."
            out.append(
                Candidate("negacion", m.start("aff"), m.end("aff"), replacement, why, counterpart)
            )
    return out


def _measure_candidates(text: str, sec: Sections, rng: random.Random) -> list[Candidate]:
    out = []
    for target, other in ((sec.conclusion, sec.findings), (sec.findings, sec.conclusion)):
        other_measures = {}
        for m in _MEASURE_RE.finditer(text, *other):
            key = (m.group("num").replace(",", "."), m.group("unit").lower())
            other_measures.setdefault(key, m.span())
        for m in _MEASURE_RE.finditer(text, *target):
            num, unit = m.group("num"), m.group("unit")
            if (num.replace(",", "."), unit.lower()) not in other_measures:
                continue
            if rng.random() < 0.5:
                new_unit = "cm" if unit.lower() == "mm" else "mm"
                new = f"{num}{m.group('sep')}{_match_case(unit, new_unit)}"
            else:
                scaled = float(num.replace(",", ".")) * 10
                new_num = f"{scaled:g}".replace(".", ",") if "," in num else f"{scaled:g}"
                new = f"{new_num}{m.group('sep')}{unit}"
            where = "los hallazgos" if target == sec.conclusion else "la conclusión"
            why = f"La medida {new} no coincide con la que figura en {where} ({num} {unit})."
            counterpart = other_measures[(num.replace(",", "."), unit.lower())]
            out.append(Candidate("medida", m.start(), m.end(), new, why, counterpart))
    return out


# Speech-recognition slips that Spanish dictation produces: the sound is kept, the
# spelling changes, so the result reads as a non-word. (regex, replacement)
_SLIPS = [
    (re.compile(r"v"), "b"),
    (re.compile(r"b"), "v"),
    (re.compile(r"ll"), "y"),
    (re.compile(r"(?<=[aeiou])y(?=[aeiou])"), "ll"),
    (re.compile(r"^h"), ""),
    (re.compile(r"^(?=[aeiou])"), "h"),
    (re.compile(r"c(?=[ei])"), "s"),
    (re.compile(r"z"), "s"),
    (re.compile(r"g(?=[ei])"), "j"),
    (re.compile(r"j(?=[ei])"), "g"),
    (re.compile(r"x"), "s"),
    (re.compile(r"qu"), "k"),
]
_VOCABULARY: set[str] = set()


def load_vocabulary(texts) -> None:
    """Words seen in the corpus. A slip is only injected if it yields an unseen word."""
    for t in texts:
        _VOCABULARY.update(_fold(w) for w in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", t))


def _transcription_candidates(text: str, sec: Sections, rng: random.Random) -> list[Candidate]:
    out = []
    span = (sec.findings[0], sec.conclusion[1])
    for m in re.finditer(r"\b[a-záéíóúñ]{7,}\b", text[span[0] : span[1]]):
        word = m.group()
        if _fold(word) in _STOPWORDS:
            continue
        slips = [(p, r) for p, r in _SLIPS if p.search(word)]
        if not slips:
            continue
        p, r = rng.choice(slips)
        hits = list(p.finditer(word))
        h = rng.choice(hits)
        new = word[: h.start()] + h.expand(r) + word[h.end() :]
        if new == word or _fold(new) in _VOCABULARY or _fold(new) in _fold(text):
            continue
        start = span[0] + m.start()
        why = f"Posible error de transcripción: «{new}» en lugar de «{word}»."
        out.append(Candidate("transcripcion", start, start + len(word), new, why))
    return out


def _discordance_candidates(text: str, sec: Sections) -> list[Candidate]:
    """Drop one conclusion sentence whose finding then appears nowhere in the conclusion."""
    concl = _sentence_spans(text, sec.conclusion)
    if len(concl) < 2:
        return []
    findings = [
        (_content_words(text[s:e]) - _GENERIC_STEMS, (s, e))
        for s, e in _sentence_spans(text, sec.findings)
    ]
    out = []
    for i, (s, e) in enumerate(concl):
        sentence = text[s:e]
        if _is_negated(sentence):  # dropping a "no X" leaves nothing to point at
            continue
        words = _content_words(sentence) - _GENERIC_STEMS
        rest = set().union(*(_content_words(text[a:b]) for j, (a, b) in enumerate(concl) if j != i))
        match = max(findings, key=lambda f: len(f[0] & words), default=None)
        if match is None or len(match[0] & words) < 2 or match[0] & rest:
            continue
        f_start, f_end = match[1]
        if _is_negated(text[f_start:f_end]):
            continue
        # Remove the sentence plus the whitespace after it.
        end = e
        while end < len(text) and text[end] in " \n\t":
            end += 1
        why = "Los hallazgos describen este hallazgo, pero la conclusión no lo recoge."
        out.append(Candidate("discordancia", s, end, "", why, None, report_at=(f_start, f_end)))
    return out


def candidates(
    text: str, rng: random.Random, types: tuple[str, ...] = ERROR_TYPES
) -> dict[str, list[Candidate]]:
    """All injectable errors of `types` for a report, grouped by type. Empty if no sections."""
    sec = split_sections(text)
    if sec is None:
        return {}
    builders = {
        "lateralidad": lambda: _lateral_candidates(text, sec),
        "negacion": lambda: _negation_candidates(text, sec),
        "medida": lambda: _measure_candidates(text, sec, rng),
        "discordancia": lambda: _discordance_candidates(text, sec),
        "transcripcion": lambda: _transcription_candidates(text, sec, rng),
    }
    found = {t: builders[t]() for t in types}
    return {k: v for k, v in found.items() if v}


def _fragment(text: str, start: int, end: int, before: int = 4, after: int = 3) -> str:
    """A few words around the changed span, clipped to its sentence.

    Always an exact substring of `text`, so evaluation can locate it in the report.
    """
    s_start = max(text.rfind(".", 0, start), text.rfind(":", 0, start)) + 1
    s_end = text.find(".", end)
    s_end = len(text) if s_end == -1 else s_end
    left = list(re.finditer(r"\S+", text[s_start:start]))[-before:]
    right = list(re.finditer(r"\S+", text[end:s_end]))[:after]
    a = s_start + left[0].start() if left else start
    b = end + right[-1].end() if right else end
    return text[a:b].strip()


def _shift(span: tuple[int, int] | None, cand: Candidate) -> tuple[int, int] | None:
    """Move a span of the original text to its position in the corrupted text."""
    if span is None or span[1] <= cand.start:
        return span
    delta = len(cand.replacement) - (cand.end - cand.start)
    return span[0] + delta, span[1] + delta


def apply(text: str, cand: Candidate) -> tuple[str, InjectedError]:
    new_text = text[: cand.start] + cand.replacement + text[cand.end :]
    start, end = cand.start, cand.start + len(cand.replacement)
    if cand.report_at is not None:
        start, end = _shift(cand.report_at, cand)
        frag = text[cand.report_at[0] : cand.report_at[1]].strip().rstrip(".")
        words = frag.split()
        # Keep the fragment short (spec: 3-12 words) and still an exact substring.
        fragmento = " ".join(words[:12]) if " ".join(words[:12]) in new_text else frag
        error = InjectedError(
            tipo=cand.tipo,
            start=start,
            end=end,
            original=text[cand.start : cand.end],
            fragmento=fragmento,
            explicacion=cand.explicacion,
        )
        return new_text, error
    if end == start:  # pure deletion ("no " removed): point at the next word instead
        nxt = re.match(r"\s*\S+", new_text[start:])
        end = start + (nxt.end() if nxt else 0)
    error = InjectedError(
        tipo=cand.tipo,
        start=start,
        end=end,
        original=text[cand.start : cand.end],
        fragmento=_fragment(new_text, start, end),
        explicacion=cand.explicacion,
        counterpart=_shift(cand.counterpart, cand),
    )
    return new_text, error


def inject(
    text: str, rng: random.Random, tipo: str | None = None, types: tuple[str, ...] = ERROR_TYPES
) -> tuple[str, InjectedError] | None:
    """Inject one error, of `tipo` if given, else of a random eligible type among `types`."""
    found = candidates(text, rng, types if tipo is None else (tipo,))
    if tipo is not None:
        found = {tipo: found[tipo]} if tipo in found else {}
    if not found:
        return None
    chosen = rng.choice(sorted(found))
    return apply(text, rng.choice(found[chosen]))


def _move(span: tuple[int, int] | None, at: int, delta: int) -> tuple[int, int] | None:
    return span if span is None or span[0] < at else (span[0] + delta, span[1] + delta)


def _overlaps(a: tuple[int, int] | None, b: tuple[int, int]) -> bool:
    return a is not None and a[0] < b[1] and b[0] < a[1]


def inject_two(
    text: str, rng: random.Random, types: tuple[str, ...] = ERROR_TYPES
) -> tuple[str, list[InjectedError]] | None:
    """Inject two errors of different types into one report (recipe v4).

    Real reports can hold more than one slip, and models trained on one error per report
    tend to stop at the first one they find. discordancia is left out: it reports the
    error away from the edit, which would make the span bookkeeping fragile.
    """
    found = candidates(text, rng, tuple(t for t in types if t != "discordancia"))
    if len(found) < 2:
        return None
    t1, t2 = rng.sample(sorted(found), 2)
    a, b = sorted((rng.choice(found[t1]), rng.choice(found[t2])), key=lambda c: c.start)
    ea, eb = (a.start, a.end), (b.start, b.end)
    if a.end > b.start or _overlaps(a.counterpart, eb) or _overlaps(b.counterpart, ea):
        return None
    # Apply the later edit first so the earlier one's offsets stay valid, then move the
    # later error by however much the earlier edit grew or shrank the text.
    text1, err_b = apply(text, b)
    db = len(b.replacement) - (b.end - b.start)
    text2, err_a = apply(text1, replace(a, counterpart=_move(a.counterpart, b.end, db)))
    da = len(a.replacement) - (a.end - a.start)
    start, end = err_b.start + da, err_b.end + da
    err_b = replace(
        err_b,
        start=start,
        end=end,
        fragmento=_fragment(text2, start, end),
        counterpart=_move(err_b.counterpart, a.end, da),
    )
    return text2, [err_a, err_b]
