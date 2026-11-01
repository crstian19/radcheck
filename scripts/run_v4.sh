#!/usr/bin/env bash
# Round 2: recipe v4 (documents with two errors) on the 4B, then GRPO run 2 on the 4B v3s
# (false alarm = -1, KL beta 0.04, CARES + synthetic mixed). Same evaluations as before.
set -uo pipefail
cd ~/radcheck
export PATH="$HOME/.local/bin:$PATH"
stamp() { echo "=== $(date '+%F %T') $*"; }
mkdir -p outputs/eval-v4 outputs/eval-grpo2

ev() {  # ev <outdir> <tag> <adapter> <data> <system>
  stamp "eval $2"
  uv run --extra cuda python -m radcheck.evaluate --backend hf --model Qwen/Qwen3.5-4B --adapter "$3" \
    --data "$4" --system "$5" --batch-size 16 --out "$1/$2.json" > "$1/$2.log" 2>&1 \
    && stamp "done $2" || stamp "FAILED $2"
}
suite() {  # suite <outdir> <name> <adapter>
  ev "$1" "$2-val" "$3" data/processed-v3/val.jsonl data
  ev "$1" "$2-injector" "$3" data/processed-v3/test.jsonl data
  ev "$1" "$2-bench" "$3" data/bench_test.jsonl extended
  ev "$1" "$2-extra" "$3" data/bench_extra.jsonl extended
  for v in pairs noheaders typos; do ev "$1" "$2-$v" "$3" "data/robustness/$v.jsonl" extended; done
}

# 1. Recipe v4 = v3s + 25% extra two-error reports + 8% pasted documents.
stamp "dataset v4"
uv run --extra cuda python -m radcheck.dataset --cares data/raw/cares --out data/processed-v4 \
  --recipe v4 --extra-reports data/synthetic/reports.jsonl > outputs/dataset-v4.log 2>&1 \
  || { stamp "FAILED dataset"; exit 1; }
stamp "train qwen35-4b-v4"
# Pasted documents reach ~2,000 tokens: raise max length so no answer gets truncated.
uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-4B --data data/processed-v4 \
  --output outputs/train/qwen35-4b-v4 --epochs 2 --eval-steps 200 --max-length 3072 \
  --batch-size 4 --grad-accum 4 --no-grad-checkpointing > outputs/train-qwen35-4b-v4.log 2>&1 \
  && suite outputs/eval-v4 qwen35-4b-v4 outputs/train/qwen35-4b-v4 \
  || stamp "FAILED train v4"

# 2. Baseline numbers for the v3s on the same suite (val, pairs, noheaders, typos missing).
for spec in "val data/processed-v3/val.jsonl data" "pairs data/robustness/pairs.jsonl extended" \
            "noheaders data/robustness/noheaders.jsonl extended" "typos data/robustness/typos.jsonl extended"; do
  set -- $spec
  ev outputs/eval-v4 "qwen35-4b-v3s-$1" outputs/train/qwen35-4b-v3s "$2" "$3"
done

# 3. GRPO run 2 from the best SFT model so far (v3s).
stamp "grpo2"
uv run --extra cuda python -m radcheck.grpo --model Qwen/Qwen3.5-4B --adapter outputs/train/qwen35-4b-v3s \
  --data data/processed-v3s/train.jsonl --output outputs/train/qwen35-4b-v3s-grpo2 --max-steps 150 \
  --beta 0.04 --clean-penalty -1 > outputs/train-qwen35-4b-v3s-grpo2.log 2>&1 \
  && suite outputs/eval-grpo2 qwen35-4b-v3s-grpo2 outputs/train/qwen35-4b-v3s-grpo2 \
  || stamp "FAILED grpo2"
stamp "V4 DONE"
