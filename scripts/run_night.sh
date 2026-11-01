#!/usr/bin/env bash
# Night run (after run_v4.sh): 1) clean discordancia labels with the 27B judge and retrain the
# 4B v4; 2) smaller Qwen3.5 (0.8B, 2B) on v4; 3) two more seeds of the 4B v4 to measure noise.
set -uo pipefail
cd ~/radcheck
export PATH="$HOME/.local/bin:$PATH"
stamp() { echo "=== $(date '+%F %T') $*"; }
mkdir -p outputs/eval-night

ev() {  # ev <tag> <model> <adapter> <data> <system>
  stamp "eval $1"
  uv run --extra cuda python -m radcheck.evaluate --backend hf --model "$2" --adapter "$3" \
    --data "$4" --system "$5" --batch-size 16 --out "outputs/eval-night/$1.json" \
    > "outputs/eval-night/$1.log" 2>&1 && stamp "done $1" || stamp "FAILED $1"
}
suite() {  # suite <tag> <model> <adapter>
  ev "$1-bench" "$2" "$3" data/bench_test.jsonl extended
  ev "$1-extra" "$2" "$3" data/bench_extra.jsonl extended
  ev "$1-pairs" "$2" "$3" data/robustness/pairs.jsonl extended
  ev "$1-val" "$2" "$3" data/processed-v3/val.jsonl data
}
train() {  # train <tag> <model> <data> [extra args]
  local tag=$1 model=$2 data=$3; shift 3
  stamp "train $tag"
  uv run --extra cuda python -m radcheck.train --model "$model" --data "$data" \
    --output "outputs/train/$tag" --epochs 2 --eval-steps 200 --max-length 3072 \
    --batch-size 4 --grad-accum 4 --no-grad-checkpointing "$@" > "outputs/train-$tag.log" 2>&1 \
    && suite "$tag" "$model" "outputs/train/$tag" || stamp "FAILED train $tag"
}

# 1. Discordancia label cleaning (27B judge with reasoning), then the 4B v4 on clean labels.
stamp "judge"
PYTHONPATH=src ~/radcheck-vllm/bin/python -m radcheck.judge --model Qwen/Qwen3.8-27B \
  --data data/processed-v4 --out data/processed-v4c > outputs/judge.log 2>&1 \
  && stamp "done judge: $(tail -12 outputs/judge.log | tr -d '\n ')" || stamp "FAILED judge"
[ -s data/processed-v4c/train.jsonl ] && train qwen35-4b-v4c Qwen/Qwen3.5-4B data/processed-v4c

# 2. How small can it go?
train qwen35-2b-v4 Qwen/Qwen3.5-2B data/processed-v4
train qwen35-0.8b-v4 Qwen/Qwen3.5-0.8B data/processed-v4

# 3. Noise: same recipe, other seeds (the first v4 used seed 42).
train qwen35-4b-v4-s7 Qwen/Qwen3.5-4B data/processed-v4 --seed 7
train qwen35-4b-v4-s13 Qwen/Qwen3.5-4B data/processed-v4 --seed 13

# 4. Filler until morning: the 9B on v4 completes the size curve (0.8B, 2B, 4B, 9B).
# One epoch and gradient checkpointing: the 9B without it at 3,072 tokens risks OOM.
stamp "train qwen35-9b-v4"
uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-9B --data data/processed-v4 \
  --output outputs/train/qwen35-9b-v4 --epochs 1 --eval-steps 200 --max-length 3072 \
  --batch-size 4 --grad-accum 4 > outputs/train-qwen35-9b-v4.log 2>&1 \
  && suite qwen35-9b-v4 Qwen/Qwen3.5-9B outputs/train/qwen35-9b-v4 || stamp "FAILED train qwen35-9b-v4"
stamp "NIGHT DONE"
