<h1 align="center"><img src="docs/img/logo.png" alt="radcheck" width="560"></h1>

A small, local LLM that reviews **Spanish radiology reports** before they are signed and flags internal inconsistencies: swapped laterality, inverted negations, implausible measurements, and findings missing from the conclusion. Think of it as a linter for radiology reports.

> **Status:** learning project, early stage. Not a medical device, not for clinical use. It only checks the internal consistency of a text; it never judges whether a finding is clinically correct.

## Why

Radiologists dictate reports with speech recognition, and small errors slip through ("derecho" vs "izquierdo", "no se observa" vs "se observa"). Hospitals cannot send real reports to hosted LLM APIs, so a useful checker has to be **small enough to run on-premises**. Prior work (Sun et al., *Radiology* 2025) showed that fine-tuned open models trained on synthetic errors can beat GPT-4 at this task, in English. radcheck explores the same idea in Spanish with small models.

## How it works

```mermaid
flowchart LR
    C[CARES<br/>Spanish radiology reports] --> S[Split by report]
    S --> I[Error injector<br/>rule-based]
    I --> D[SFT dataset<br/>50% clean / 50% with errors]
    D --> FT[LoRA fine-tune<br/>Qwen3 / Salamandra]
    FT --> E[Evaluation<br/>synthetic + radiologist test sets]
    E --> G[GGUF + llama-server]
```

Input: the text of a report. Output: JSON listing the problems found (or an empty list).

```json
{"errores": [{"tipo": "lateralidad", "fragmento": "derrame pleural izquierdo",
  "explicacion": "Los hallazgos describen el derrame en el lado derecho."}]}
```

## Quick start

```bash
# AMD GPU (ROCm 7.2)
uv sync --extra rocm --group dev
# NVIDIA GPU (CUDA 13.0, incl. Blackwell)
uv sync --extra cuda --group dev

uv run --extra rocm python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Pass the extra to **every** `uv sync` and `uv run`. A bare `uv run` re-syncs the environment without the extra and silently swaps in the default PyPI (CUDA) build of torch. See [Development](./docs/development.md#the-extra-trap).

## Model

Private for now, CC BY-NC-SA 4.0 (inherited from CARES). Each repo holds one model family; every training recipe is a commit + git tag (`v1`, `v2`, ...), `main` is the latest, and `revision="v1"` loads an older one. Uploaded with `python -m radcheck.publish`.

| Repo | What | Versions | RadCheck-Bench-ES F1 |
|---|---|---|---|
| [radcheck-qwen35-4b-lora-es](https://huggingface.co/Crstian19/radcheck-qwen35-4b-lora-es) | LoRA for Qwen3.5-4B | v1, **v2** | 0.896, **0.929** |
| [radcheck-qwen35-4b-gguf-es](https://huggingface.co/Crstian19/radcheck-qwen35-4b-gguf-es) | v2 merged, Q4_K_M / Q8_0 for llama.cpp (runs on a 16 GB GPU) | v2 | (Q4_K_M of v1: 0.894) |
| [radcheck-qwen38-27b-lora-es](https://huggingface.co/Crstian19/radcheck-qwen38-27b-lora-es) | LoRA for Qwen3.8-27B (best quality) | v1, **v2** | 0.979, **0.979** |
| [radcheck-qwen3-4b-lora-es](https://huggingface.co/Crstian19/radcheck-qwen3-4b-lora-es) | First model, LoRA for Qwen3-4B | v0.1 | — |

![F1 by model](./docs/img/f1-injector-vs-bench.png)

## Documentation

| Doc | Content |
|---|---|
| [Architecture](./docs/architecture.md) | Task definition, error taxonomy, data pipeline, models, metrics |
| [Data](./docs/data.md) | Datasets, licences, and the rules about patient data |
| [Development](./docs/development.md) | Environment on AMD (ROCm) and NVIDIA (CUDA), commands, layout |
| [Benchmark spec](./docs/benchmark-spec.md) | RadCheck-Bench-ES: independent evaluation set, brief for the agent that builds it |

## Licence

Code: [MIT](./LICENSE). Data and any model trained on CARES inherit **CC BY-NC-SA 4.0** (non-commercial, share-alike). See [docs/data.md](./docs/data.md).
