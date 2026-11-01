#!/usr/bin/env bash
# QLoRA vs LoRA: the 4B v4 recipe exactly as before (seed 42), but the frozen base in NF4.
# Waits for run_day.sh. Logs peak GPU memory so both memory and quality can be compared.
set -uo pipefail
cd ~/radcheck
export PATH="$HOME/.local/bin:$PATH"
stamp() { echo "=== $(date '+%F %T') $*"; }
until grep -q "DAY DONE" outputs/day-chain.log 2>/dev/null; do sleep 120; done
mkdir -p outputs/eval-qlora
ev() {
  stamp "eval $1"
  uv run --extra cuda python -m radcheck.evaluate --backend hf --model Qwen/Qwen3.5-4B \
    --adapter outputs/train/qwen35-4b-v4-qlora --data "$2" --system "$3" --batch-size 16 \
    --out "outputs/eval-qlora/$1.json" > "outputs/eval-qlora/$1.log" 2>&1 && stamp "done $1" || stamp "FAILED $1"
}
stamp "train qwen35-4b-v4-qlora"
nvidia-smi --query-gpu=timestamp,memory.used,utilization.gpu --format=csv,noheader -l 30 \
  > outputs/qlora-gpu.csv & smi=$!
uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-4B --data data/processed-v4 \
  --output outputs/train/qwen35-4b-v4-qlora --epochs 2 --eval-steps 200 --max-length 3072 \
  --batch-size 4 --grad-accum 4 --no-grad-checkpointing --load-in-4bit \
  > outputs/train-qwen35-4b-v4-qlora.log 2>&1; rc=$?
kill $smi
stamp "peak GPU memory: $(cut -d, -f2 outputs/qlora-gpu.csv | sort -n | tail -1)"
# The adapter is evaluated on the bf16 base, as it would be deployed (and as the LoRA was).
[ $rc -eq 0 ] && {
  ev qwen35-4b-v4-qlora-bench data/bench_test.jsonl extended
  ev qwen35-4b-v4-qlora-extra data/bench_extra.jsonl extended
  ev qwen35-4b-v4-qlora-pairs data/robustness/pairs.jsonl extended
  ev qwen35-4b-v4-qlora-val data/processed-v3/val.jsonl data
  ev qwen35-4b-v4-qlora-injector data/processed-v3/test.jsonl data
} || stamp "FAILED train qlora"
stamp "QLORA DONE"
