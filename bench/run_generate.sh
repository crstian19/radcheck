#!/usr/bin/env bash
# Run bench/generate.py with credentials resolved at runtime from the local model config.
# Nothing here writes a secret to disk; the key lives only in the process environment.
# Endpoint and provider names come from the environment, not from this file:
#   RADCHECK_BENCH_BASE_URL  OpenAI-compatible endpoint of the generator
#   RADCHECK_KEY_PROVIDERS   provider names to look up in the model config (first match wins)
set -euo pipefail
: "${RADCHECK_BENCH_BASE_URL:?set RADCHECK_BENCH_BASE_URL}"
: "${RADCHECK_KEY_PROVIDERS:?set RADCHECK_KEY_PROVIDERS}"
export RADCHECK_KEY_PROVIDERS
cd "$(dirname "$0")/.."

KEY=$(python3 - <<'PY'
import os, pathlib, re
cfg = pathlib.Path.home() / ".omp" / "agent" / "models.yml"
text = cfg.read_text()
for provider in os.environ["RADCHECK_KEY_PROVIDERS"].split():
    m = re.search(rf"^  {provider}:\n(?:(?!^  \S).)*?^\s+apiKey:\s*(\S+)", text, re.M | re.S)
    if m:
        print(m.group(1))
        break
PY
)
if [ -z "$KEY" ]; then echo "no key found" >&2; exit 1; fi

export DEEPSEEK_API_KEY="$KEY"
export RADCHECK_BENCH_MODEL="${RADCHECK_BENCH_MODEL:-deepseek-v4-flash}"

exec .venv/bin/python bench/generate.py generate "$@"
