"""radcheck demo: paste a Spanish radiology report, get its internal inconsistencies.

Runs the quantised Qwen3.5-4B fine-tune (GGUF) with llama.cpp's llama-server on CPU and
shows the flagged fragments highlighted in the report. Synthetic reports only: never paste
real patient data here.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.request
from pathlib import Path

import gradio as gr
from huggingface_hub import hf_hub_download

MODEL_REPO = os.environ.get("MODEL_REPO", "Crstian19/radcheck-qwen35-4b-gguf-es")
MODEL_FILE = os.environ.get("MODEL_FILE", "radcheck-qwen35-4b-v4.1-Q4_K_M.gguf")
SERVER = "http://127.0.0.1:8080"

# Must match src/radcheck/prompts.py SYSTEM_PROMPT_EXTENDED (the model was trained with it).
SYSTEM_PROMPT = """Eres un asistente que revisa informes radiológicos en español antes de su firma.
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

COLORS = {
    "lateralidad": "#2a78d6",
    "negacion": "#eb6834",
    "medida": "#1baf7a",
    "discordancia": "#8a5cf5",
    "transcripcion": "#d1a20f",
}


def start_server() -> None:
    path = hf_hub_download(MODEL_REPO, MODEL_FILE, token=os.environ.get("HF_TOKEN"))
    cmd = ["/opt/llama/llama-server", "-m", path, "--jinja", "-c", "8192", "--host", "127.0.0.1"]
    # os.cpu_count() reports the host's cores, not the Space's 2 vCPU quota.
    cmd += ["--port", "8080", "-t", os.environ.get("N_THREADS", "2")]
    subprocess.Popen(cmd)
    for _ in range(300):
        try:
            urllib.request.urlopen(f"{SERVER}/health", timeout=2)
            return
        except OSError:
            time.sleep(1)
    raise RuntimeError("llama-server did not start")


def ask(report: str) -> str:
    body = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": report},
        ],
        "temperature": 0,
        "max_tokens": 512,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        f"{SERVER}/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["choices"][0]["message"]["content"] or ""


def parse(text: str) -> list[dict] | None:
    """First JSON object with an "errores" list in the answer (same rule as evaluation)."""
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch == "{":
            try:
                obj, _ = decoder.raw_decode(text, i)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and isinstance(obj.get("errores"), list):
                return [e for e in obj["errores"] if isinstance(e, dict)]
    return None


def locate(fragment: str, report: str) -> tuple[int, int] | None:
    i = report.find(fragment)
    if i != -1:
        return i, i + len(fragment)
    pattern = r"\s+".join(re.escape(t) for t in fragment.split())
    m = re.search(pattern, report, re.IGNORECASE) if pattern else None
    return m.span() if m else None


def analyze(report: str):
    report = report.strip()
    if not report:
        return [], [], "Paste a report."
    t0 = time.time()
    raw = ask(report)
    errors = parse(raw)
    took = f"{time.time() - t0:.1f} s"
    if errors is None:
        return [(report, None)], [], f"Invalid model answer ({took}): {raw[:200]}"
    spans = sorted(
        (span, e.get("tipo", "?"))
        for e in errors
        if (span := locate(str(e.get("fragmento", "")), report))
    )
    highlighted, pos = [], 0
    for (start, end), tipo in spans:
        if start < pos:  # overlapping flags: keep the first
            continue
        highlighted += [(report[pos:start], None), (report[start:end], tipo)]
        pos = end
    highlighted.append((report[pos:], None))
    rows = [[e.get("tipo", ""), e.get("fragmento", ""), e.get("explicacion", "")] for e in errors]
    status = f"{len(errors)} inconsistencies in {took}." if errors else f"None found ({took})."
    return highlighted, rows, status


EXAMPLES = json.loads((Path(__file__).parent / "examples.json").read_text(encoding="utf-8"))

with gr.Blocks(title="radcheck") as demo:
    gr.Markdown(
        "# radcheck\n"
        "Flags **internal inconsistencies** in Spanish radiology reports: laterality, negation, "
        "measurements, findings missing from the conclusion and dictation slips. Qwen3.5-4B "
        "fine-tuned with LoRA (v4.1, Q4 quantised) on a free CPU, so expect ~30-60 s per report. "
        "Reports and explanations are in Spanish.\n\n"
        "> Research preview, **not validated by a physician**. Not a medical device. "
        "**Never paste real patient data.**"
    )
    report = gr.Textbox(
        label="Report (Spanish)", lines=12, placeholder="HALLAZGOS: ... CONCLUSIÓN: ..."
    )
    button = gr.Button("Check", variant="primary")
    status = gr.Markdown()
    marked = gr.HighlightedText(label="Flagged report", color_map=COLORS)
    table = gr.Dataframe(headers=["type", "fragment", "explanation"], label="Inconsistencies")
    gr.Examples(EXAMPLES, inputs=report, label="Synthetic examples (RadCheck-Bench-ES dev)")
    button.click(analyze, inputs=report, outputs=[marked, table, status])

if __name__ == "__main__":
    start_server()
    demo.launch(server_name="0.0.0.0", server_port=7860)
