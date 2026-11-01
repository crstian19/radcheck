#!/usr/bin/env bash
# Independent verification with a model from a DIFFERENT family than the generator.
# Endpoint, model and provider name come from the environment:
#   RADCHECK_BENCH_CHECK_BASE_URL, RADCHECK_BENCH_CHECK_MODEL, RADCHECK_CHECK_PROVIDER
set -euo pipefail
: "${RADCHECK_BENCH_CHECK_BASE_URL:?set RADCHECK_BENCH_CHECK_BASE_URL}"
: "${RADCHECK_BENCH_CHECK_MODEL:?set RADCHECK_BENCH_CHECK_MODEL}"
: "${RADCHECK_CHECK_PROVIDER:?set RADCHECK_CHECK_PROVIDER}"
export RADCHECK_CHECK_PROVIDER
cd "$(dirname "$0")/.."

KEY=$(python3 - <<'PY'
import os, pathlib, re
cfg = pathlib.Path.home() / ".omp" / "agent" / "models.yml"
text = cfg.read_text()
provider = os.environ["RADCHECK_CHECK_PROVIDER"]
m = re.search(rf"^  {provider}:\n(?:(?!^  \S).)*?^\s+apiKey:\s*(\S+)", text, re.M | re.S)
print(m.group(1) if m else "")
PY
)
if [ -z "$KEY" ]; then echo "no key found" >&2; exit 1; fi

export RADCHECK_CHECK_KEY="$KEY"
export RADCHECK_BENCH_CHECK_KEY_VAR="RADCHECK_CHECK_KEY"

exec .venv/bin/python bench/check.py "$@"
