#!/usr/bin/env bash
# Morning filler: the 9B v4 with 2 epochs (the 1-epoch run looked undertrained: best val,
# but bench below the 4B). Same suite as run_night.sh.
set -uo pipefail
cd ~/radcheck
export PATH="$HOME/.local/bin:$PATH"
stamp() { echo "=== $(date '+%F %T') $*"; }
ev() {
  stamp "eval $1"
  uv run --extra cuda python -m radcheck.evaluate --backend hf --model Qwen/Qwen3.5-9B --adapter outputs/train/qwen35-9b-v4-e2 \
    --data "$2" --system "$3" --batch-size 16 --out "outputs/eval-night/$1.json" \
    > "outputs/eval-night/$1.log" 2>&1 && stamp "done $1" || stamp "FAILED $1"
}
stamp "train qwen35-9b-v4-e2"
uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-9B --data data/processed-v4 \
  --output outputs/train/qwen35-9b-v4-e2 --epochs 2 --eval-steps 200 --max-length 3072 \
  --batch-size 4 --grad-accum 4 > outputs/train-qwen35-9b-v4-e2.log 2>&1 && {
  ev qwen35-9b-v4-e2-bench data/bench_test.jsonl extended
  ev qwen35-9b-v4-e2-extra data/bench_extra.jsonl extended
  ev qwen35-9b-v4-e2-pairs data/robustness/pairs.jsonl extended
  ev qwen35-9b-v4-e2-val data/processed-v3/val.jsonl data
} || stamp "FAILED train qwen35-9b-v4-e2"
stamp "MORNING DONE"
