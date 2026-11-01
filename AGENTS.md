# AGENTS.md

Learning project: fine-tune a small LLM to flag internal inconsistencies in Spanish radiology reports. The owner is new to ML: explain ML decisions briefly when making them.

## Rules

- **No real patient data, ever** (not in code, tests, fixtures, prompts, or API calls). Test fixtures use invented reports.
- Nothing under `data/`, `outputs/`, `models/` is committed. CARES is CC BY-NC-SA 4.0.
- Code, comments and docs in English. Report text, labels (`tipo`) and explanations are Spanish.
- Pass the GPU extra to **every** uv command: `uv sync --extra rocm`, `uv run --extra rocm ...` (`cuda` on NVIDIA). A bare `uv run` re-syncs without it and replaces torch with the PyPI CUDA build.
- Check library APIs with Context7 before using them (transformers 5.x, TRL 1.x and PEFT change often).
- Split datasets by original report **before** injecting errors (see docs/architecture.md).

## Commands

```bash
uv sync --extra rocm --group dev
uv run --extra rocm pytest
uv run --extra rocm ruff check . && uv run --extra rocm ruff format .
```

## Docs

- [docs/architecture.md](./docs/architecture.md): task, error taxonomy, pipeline, metrics, milestones
- [docs/data.md](./docs/data.md): datasets, licences, patient-data rules
- [docs/development.md](./docs/development.md): ROCm/CUDA environment
- Owner's notes (Spanish, Obsidian): `~/Documents/obsidian-vault/Programming/Projects/radcheck/`
