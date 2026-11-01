#!/usr/bin/env bash
# Day run: 1) missing evaluations of the published 9B v4; 2) recipe v5 (more discordancia
# positives, the opposite of v4c) on the 4B; 3) a second seed of the 9B v4 (2 epochs);
# 4) missing evaluations of v4c and the 4B seeds.
set -uo pipefail
cd ~/radcheck
export PATH="$HOME/.local/bin:$PATH"
stamp() { echo "=== $(date '+%F %T') $*"; }
mkdir -p outputs/eval-day
ev() {  # ev <tag> <model> <adapter> <data> <system>
  stamp "eval $1"
  uv run --extra cuda python -m radcheck.evaluate --backend hf --model "$2" --adapter "$3" \
    --data "$4" --system "$5" --batch-size 16 --out "outputs/eval-day/$1.json" \
    > "outputs/eval-day/$1.log" 2>&1 && stamp "done $1" || stamp "FAILED $1"
}
rest() {  # rest <tag> <model> <adapter>: injector, no headers, typos
  ev "$1-injector" "$2" "$3" data/processed-v3/test.jsonl data
  ev "$1-noheaders" "$2" "$3" data/robustness/noheaders.jsonl extended
  ev "$1-typos" "$2" "$3" data/robustness/typos.jsonl extended
}
suite() {  # suite <tag> <model> <adapter>
  ev "$1-bench" "$2" "$3" data/bench_test.jsonl extended
  ev "$1-extra" "$2" "$3" data/bench_extra.jsonl extended
  ev "$1-pairs" "$2" "$3" data/robustness/pairs.jsonl extended
  ev "$1-val" "$2" "$3" data/processed-v3/val.jsonl data
  rest "$@"
}

# 1. The published 9B v4.
rest qwen35-9b-v4-e2 Qwen/Qwen3.5-9B outputs/train/qwen35-9b-v4-e2

# 2. Recipe v5 on the 4B.
stamp "dataset v5"
uv run --extra cuda python -m radcheck.dataset --cares data/raw/cares --out data/processed-v5 \
  --recipe v5 --extra-reports data/synthetic/reports.jsonl > outputs/dataset-v5.log 2>&1 \
  && { stamp "train qwen35-4b-v5"
       uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-4B --data data/processed-v5 \
         --output outputs/train/qwen35-4b-v5 --epochs 2 --eval-steps 200 --max-length 3072 \
         --batch-size 4 --grad-accum 4 --no-grad-checkpointing > outputs/train-qwen35-4b-v5.log 2>&1 \
         && suite qwen35-4b-v5 Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v5 || stamp "FAILED train v5"; } \
  || stamp "FAILED dataset v5"

# 3. Second seed of the 9B v4 (2 epochs): is 0.965 above the noise?
stamp "train qwen35-9b-v4-e2-s7"
uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-9B --data data/processed-v4 \
  --output outputs/train/qwen35-9b-v4-e2-s7 --epochs 2 --eval-steps 200 --max-length 3072 \
  --batch-size 4 --grad-accum 4 --seed 7 > outputs/train-qwen35-9b-v4-e2-s7.log 2>&1 \
  && { for d in "bench data/bench_test.jsonl extended" "extra data/bench_extra.jsonl extended" \
                "pairs data/robustness/pairs.jsonl extended" "val data/processed-v3/val.jsonl data"; do
         set -- $d; ev "qwen35-9b-v4-e2-s7-$1" Qwen/Qwen3.5-9B outputs/train/qwen35-9b-v4-e2-s7 "$2" "$3"
       done; } || stamp "FAILED train 9b s7"

# 4. Missing evaluations of last night's 4B models.
rest qwen35-4b-v4c Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v4c
rest qwen35-4b-v4-s7 Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v4-s7
rest qwen35-4b-v4-s13 Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v4-s13
stamp "DAY DONE"
