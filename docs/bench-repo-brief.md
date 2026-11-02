# Brief: make RadCheck-Bench-ES a standalone GitHub repository

Self-contained task for an agent. Read all of it before changing anything.

## Goal

Turn the benchmark that lives in `~/Dev/radcheck/bench/` into a **standalone, English,
GitHub-ready repository** at `~/Dev/radcheck-bench-es/`, so the owner can create the GitHub
repo and push it himself.

## Hard rules

1. **Do not modify anything under `~/Dev/radcheck/`.** Copy from it; work only in
   `~/Dev/radcheck-bench-es/`.
2. **Do not create a GitHub repository, add a remote, push or publish anything.** You may run
   `git init` and stage files, but **do not commit**: the owner reviews and commits.
3. **No secrets.** The API key is read from `DEEPSEEK_API_KEY` at run time. Make sure no key,
   token, gateway URL with credentials, or private hostname appears in any file, log or
   notebook. Run a secret scan (e.g. `gitleaks detect --no-git` if available, otherwise grep for
   `sk-`, `api_key`, `token`, `Bearer`, `password`) and report the result.
4. **English everywhere**, except what must stay Spanish by nature: the reports, labels
   (`tipo` values: `lateralidad`, `negacion`, `medida`, `discordancia`, `transcripcion`),
   explanations, the system prompt the models are evaluated with, the generation prompt
   templates actually used (keep them byte-identical; add an English summary next to each), and
   `radiologist_review.md` (it is for a Spanish radiologist; add a one-line English note on top).
5. Do not regenerate data or call any API. The data files are final (`v1`); copy them as is and
   verify with checksums that they are byte-identical to the originals.
6. No real patient data; no CARES text (the benchmark never used CARES; keep it that way).

## What the repository must contain

```
radcheck-bench-es/
├── README.md              # from bench/README.md (already English); adapt paths to this repo
├── LICENSE-DATA           # CC BY 4.0 for the data (full text or official link + summary)
├── LICENSE                # MIT for the code
├── CITATION.cff           # title, version 1.0.0, date 2026-10-31, author "Cristian Gutiérrez",
│                          # licence CC-BY-4.0, repository-code placeholder URL
├── CHANGELOG.md           # v1.0.0
├── data/
│   ├── dev.jsonl  test.jsonl  extra.jsonl   # = radcheck_bench_v1_{dev,test,extra}.jsonl
│   ├── raw.jsonl  specs.jsonl  review.jsonl  stats.json
│   └── SHA256SUMS
├── report/report.html     # self-contained web report
├── review/radiologist_review.md
├── prompts/               # templates used + MODEL.md, plus English summaries
├── scripts/               # generate.py validate.py build.py check.py report.py + run_*.sh
├── evaluate/              # a small, dependency-light scorer (see below)
├── pyproject.toml         # uv project, Python >= 3.12, minimal deps; no torch
└── .gitignore             # .env, __pycache__, .venv, logs, any local cache
```

### Standalone scorer

Today the benchmark is scored by `radcheck.metrics` / `radcheck.evaluate` in the radcheck
repo. Add `evaluate/score.py` so others can score **their own model's predictions** without
radcheck:

- Input: `data/test.jsonl` and a JSONL of predictions `{"id": ..., "output": "<raw model text>"}`.
- Parse the first JSON object with an `"errores"` list (same rule as
  `~/Dev/radcheck/src/radcheck/prompts.py::parse_output`).
- Score exactly like `~/Dev/radcheck/src/radcheck/metrics.py` (type must match; the fragment
  must overlap the gold span or its counterpart; report precision, recall, F1 overall and per
  type, false-alarm rate on clean reports, detection rate, invalid-JSON rate). Port the logic,
  do not import radcheck.
- Add a tiny test with 3 handcrafted predictions that checks the numbers.
- Optional: `evaluate/run_openai.py` that queries any OpenAI-compatible endpoint (vLLM,
  llama-server) with the system prompt and writes the predictions file.

### README additions

- A "Quick start: evaluate your model" section using the scorer.
- A "Results" section with this table (RadCheck-Bench-ES v1 test, F1 / false alarms), stating
  the models were fine-tuned by the radcheck project and are not public yet:

| Model | F1 | False alarms |
|---|---|---|
| Qwen3.8-27B, no fine-tune | 0.778 | 1.2% |
| radcheck Qwen3.5-4B v1 | 0.896 | 1.2% |
| radcheck Qwen3.5-4B v2 | 0.929 | 0.0% |
| radcheck Qwen3.5-4B v3 | 0.942 | 0.0% |
| radcheck Qwen3.6-35B-A3B v1 | 0.967 | 0.6% |
| Gemma 4 31B + LoRA | 0.967 | 0.0% |
| radcheck Qwen3.8-27B v2 | 0.979 | 0.0% |

- Hugging Face mirror: `Crstian19/radcheck-bench-es` (public).
- "Citation" section pointing to `CITATION.cff`.

## Acceptance

- [ ] `uv run python evaluate/score.py --data data/test.jsonl --pred <file>` works, and its test passes.
- [ ] `SHA256SUMS` matches the original files in `~/Dev/radcheck/bench/`.
- [ ] Secret scan clean; result reported.
- [ ] Everything English except the items listed in rule 4.
- [ ] `git status` shows the staged files; nothing committed, no remote.
- [ ] Final message: a short summary, the tree, the secret-scan output, and anything you were
      unsure about.
