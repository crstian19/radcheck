"""Prompt format shared by training and evaluation, and parsing of model output."""

from __future__ import annotations

import json
import re

SYSTEM_PROMPT = """Eres un asistente que revisa informes radiológicos en español antes de su firma.
Busca solo incoherencias internas del texto entre los hallazgos y la conclusión:
- lateralidad: el mismo hallazgo aparece en lados distintos (derecho/izquierdo).
- negacion: una parte afirma lo que otra niega.
- medida: la misma medida no coincide (cifra o unidad).
No valores si los hallazgos son clínicamente correctos ni sugieras diagnósticos.

Responde únicamente con JSON, con este formato:
{"errores": [{"tipo": "lateralidad|negacion|medida", "fragmento": "texto exacto copiado del informe", "explicacion": "una frase"}]}
Si no hay incoherencias, responde {"errores": []}."""

# Recipe v3: two more types. Kept apart so v1/v2 models and RadCheck-Bench-ES (which
# embeds SYSTEM_PROMPT verbatim) stay comparable.
SYSTEM_PROMPT_EXTENDED = """Eres un asistente que revisa informes radiológicos en español antes de su firma.
Busca solo errores del propio texto:
- lateralidad: el mismo hallazgo aparece en lados distintos (derecho/izquierdo).
- negacion: una parte afirma lo que otra niega.
- medida: la misma medida no coincide (cifra o unidad).
- discordancia: un hallazgo descrito en los hallazgos no aparece en la conclusión.
- transcripcion: una palabra mal escrita por el dictado por voz.
No valores si los hallazgos son clínicamente correctos ni sugieras diagnósticos.

Responde únicamente con JSON, con este formato:
{"errores": [{"tipo": "lateralidad|negacion|medida|discordancia|transcripcion", "fragmento": "texto exacto copiado del informe", "explicacion": "una frase"}]}
Si no hay errores, responde {"errores": []}."""

# Qwen3 chat templates think by default; the task needs a direct JSON answer.
CHAT_TEMPLATE_KWARGS = {"enable_thinking": False}


def prompt_messages(report: str, system: str = SYSTEM_PROMPT) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": report},
    ]


def answer(errors: list[dict[str, str]]) -> str:
    """Canonical assistant answer used as the training target."""
    return json.dumps({"errores": errors}, ensure_ascii=False)


_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def parse_output(text: str) -> list[dict[str, str]] | None:
    """Extract the list of errors from a model answer. None if it is not valid JSON."""
    text = _THINK_RE.sub("", text)
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("errores"), list):
            return [e for e in obj["errores"] if isinstance(e, dict)]
    return None
