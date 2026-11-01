"""Convert the radiologist's hand-written reports into the evaluation JSONL format.

Input format (one block per report, see the vault note "Kit para el radiólogo"):

    ### Informe 017
    EXPLORACIÓN: ...
    HALLAZGOS: ...
    CONCLUSIÓN: ...

    CLAVE:
    - tipo: lateralidad
      dónde: "lóbulo superior izquierdo" (conclusión)
      explicación: en hallazgos está en el lóbulo superior derecho

A correct report uses `CLAVE: ninguno`.

Usage:
    uv run --extra rocm python -m radcheck.radiologist data/radiologist/informes.md \
        --out data/radiologist/test.jsonl
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path

from radcheck.metrics import locate
from radcheck.prompts import CHAT_TEMPLATE_KWARGS, answer, prompt_messages

_BLOCK_RE = re.compile(r"^###\s*Informe\s+(\S+)\s*$", re.MULTILINE | re.IGNORECASE)
_KEY_RE = re.compile(r"^\s*CLAVE\s*:(.*)$", re.MULTILINE | re.IGNORECASE | re.DOTALL)
_ITEM_RE = re.compile(r"^\s*-\s*tipo\s*:", re.MULTILINE | re.IGNORECASE)
_FIELD_RE = re.compile(r"^\s*-?\s*(tipo|d[oó]nde|explicaci[oó]n)\s*:\s*(.+?)\s*$", re.IGNORECASE)


class FormatError(ValueError):
    pass


def _fold(s: str) -> str:
    s = unicodedata.normalize("NFD", s.strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _parse_key(block_id: str, key: str, report: str) -> list[dict]:
    if _fold(key).startswith("ninguno"):
        return []
    gold = []
    for chunk in _ITEM_RE.split(key)[1:]:
        fields = {}
        for line in ("tipo:" + chunk).splitlines():
            m = _FIELD_RE.match(line)
            if m:
                fields[_fold(m.group(1))] = m.group(2)
        quoted = re.search(r"[\"“«](.+?)[\"”»]", fields.get("donde", ""))
        if not quoted:
            raise FormatError(f"Informe {block_id}: 'dónde' needs the quoted text from the report")
        span = locate(quoted.group(1), report)
        if span is None:
            raise FormatError(f"Informe {block_id}: {quoted.group(1)!r} is not in the report text")
        gold.append(
            {
                "tipo": _fold(fields.get("tipo", "")).replace(" ", "_"),
                "fragmento": report[span[0] : span[1]],
                "explicacion": fields.get("explicacion", ""),
                "start": span[0],
                "end": span[1],
            }
        )
    if not gold:
        raise FormatError(f"Informe {block_id}: CLAVE is neither 'ninguno' nor a list of errors")
    return gold


def parse(text: str) -> list[dict]:
    """Parse the whole document into examples (same shape as data/processed/*.jsonl)."""
    heads = list(_BLOCK_RE.finditer(text))
    examples = []
    for head, nxt in zip(heads, [*heads[1:], None]):
        block_id = head.group(1)
        body = text[head.end() : nxt.start() if nxt else len(text)]
        key = _KEY_RE.search(body)
        if key is None:
            raise FormatError(f"Informe {block_id}: missing CLAVE")
        # CARES reports are single-line; join the radiologist's lines the same way.
        report = " ".join(line.strip() for line in body[: key.start()].splitlines() if line.strip())
        gold = _parse_key(block_id, key.group(1), report)
        target = [{k: g[k] for k in ("tipo", "fragmento", "explicacion")} for g in gold]
        examples.append(
            {
                "id": f"rad-{block_id}",
                "report_id": f"rad-{block_id}",
                "prompt": prompt_messages(report),
                "completion": [{"role": "assistant", "content": answer(target)}],
                "chat_template_kwargs": CHAT_TEMPLATE_KWARGS,
                "gold": gold,
            }
        )
    return examples


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("source", help="Markdown/text file with the reports")
    ap.add_argument("--out", default="data/radiologist/test.jsonl")
    args = ap.parse_args()
    examples = parse(Path(args.source).read_text(encoding="utf-8"))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.writelines(json.dumps(ex, ensure_ascii=False) + "\n" for ex in examples)
    with_errors = sum(1 for ex in examples if ex["gold"])
    print(f"{len(examples)} reports ({with_errors} with errors) -> {args.out}")


if __name__ == "__main__":
    main()
