#!/usr/bin/env bash
# Evening/night run (1-nov): 1) soups of the seed adapters (4B x3, 9B x2); 2) 4B v4 with a
# short reasoning before the JSON, distilled from the 27B (v4r); 3) Qwen3.8-27B on v4 with
# QLoRA (here the weights matter); 4) third seed of the 9B v4.
set -uo pipefail
cd ~/radcheck
export PATH="$HOME/.local/bin:$PATH"
stamp() { echo "=== $(date '+%F %T') $*"; }
mkdir -p outputs/eval-extra
ev() {  # ev <tag> <model> <adapter> <data> <system> [extra evaluate args]
  local tag=$1 model=$2 adapter=$3 data=$4 system=$5; shift 5
  stamp "eval $tag"
  uv run --extra cuda python -m radcheck.evaluate --backend hf --model "$model" --adapter "$adapter" \
    --data "$data" --system "$system" --batch-size 16 --out "outputs/eval-extra/$tag.json" "$@" \
    > "outputs/eval-extra/$tag.log" 2>&1 && stamp "done $tag" || stamp "FAILED $tag"
}
core() {  # core <tag> <model> <adapter> [extra]: bench, extra, pairs, val
  local tag=$1 m=$2 a=$3; shift 3
  ev "$tag-bench" "$m" "$a" data/bench_test.jsonl extended "$@"
  ev "$tag-extra" "$m" "$a" data/bench_extra.jsonl extended "$@"
  ev "$tag-pairs" "$m" "$a" data/robustness/pairs.jsonl extended "$@"
  ev "$tag-val" "$m" "$a" data/processed-v3/val.jsonl data "$@"
}
suite() {  # suite <tag> <model> <adapter> [extra]: core + injector, no headers, typos
  local tag=$1 m=$2 a=$3; shift 3
  core "$tag" "$m" "$a" "$@"
  ev "$tag-injector" "$m" "$a" data/processed-v3/test.jsonl data "$@"
  ev "$tag-noheaders" "$m" "$a" data/robustness/noheaders.jsonl extended "$@"
  ev "$tag-typos" "$m" "$a" data/robustness/typos.jsonl extended "$@"
}

# 1. Soups: average the seed adapters (exact, PEFT "cat").
stamp "soup 4b"
uv run --extra cuda python -m radcheck.soup --model Qwen/Qwen3.5-4B --adapters outputs/train/qwen35-4b-v4 \
  outputs/train/qwen35-4b-v4-s7 outputs/train/qwen35-4b-v4-s13 --out outputs/train/qwen35-4b-v4-soup \
  > outputs/soup-4b.log 2>&1 && suite qwen35-4b-v4-soup Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v4-soup \
  || stamp "FAILED soup 4b"
stamp "soup 9b"
uv run --extra cuda python -m radcheck.soup --model Qwen/Qwen3.5-9B --adapters outputs/train/qwen35-9b-v4-e2 \
  outputs/train/qwen35-9b-v4-e2-s7 --out outputs/train/qwen35-9b-v4-soup \
  > outputs/soup-9b.log 2>&1 && suite qwen35-9b-v4-soup Qwen/Qwen3.5-9B outputs/train/qwen35-9b-v4-soup \
  || stamp "FAILED soup 9b"

# 2. Distilled reasoning: the 27B writes a short analysis for every answer; the 4B learns it.
stamp "rationale"
PYTHONPATH=src ~/radcheck-vllm/bin/python -m radcheck.rationale --data data/processed-v4 \
  --out data/processed-v4r > outputs/rationale.log 2>&1 \
  && { stamp "done rationale: $(tail -4 outputs/rationale.log | tr -d '\n ')"
       stamp "train qwen35-4b-v4r"
       uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-4B --data data/processed-v4r \
         --output outputs/train/qwen35-4b-v4r --epochs 2 --eval-steps 200 --max-length 3072 \
         --batch-size 4 --grad-accum 4 --no-grad-checkpointing > outputs/train-qwen35-4b-v4r.log 2>&1 \
         && suite qwen35-4b-v4r Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v4r --max-new-tokens 768 \
         || stamp "FAILED train v4r"; } \
  || stamp "FAILED rationale"

# 3. The 27B on v4 with QLoRA: 54 GB of bf16 weights, so 4 bits + gradient checkpointing.
stamp "train qwen38-27b-v4-qlora"
uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.8-27B --data data/processed-v4 \
  --output outputs/train/qwen38-27b-v4-qlora --epochs 1 --eval-steps 200 --max-length 3072 \
  --batch-size 4 --grad-accum 4 --load-in-4bit > outputs/train-qwen38-27b-v4-qlora.log 2>&1 \
  && suite qwen38-27b-v4-qlora Qwen/Qwen3.8-27B outputs/train/qwen38-27b-v4-qlora --batch-size 8 \
  || stamp "FAILED train 27b"

# 4. Third seed of the 9B v4 (2 epochs).
stamp "train qwen35-9b-v4-e2-s13"
uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-9B --data data/processed-v4 \
  --output outputs/train/qwen35-9b-v4-e2-s13 --epochs 2 --eval-steps 200 --max-length 3072 \
  --batch-size 4 --grad-accum 4 --seed 13 > outputs/train-qwen35-9b-v4-e2-s13.log 2>&1 \
  && core qwen35-9b-v4-e2-s13 Qwen/Qwen3.5-9B outputs/train/qwen35-9b-v4-e2-s13 \
  || stamp "FAILED train 9b s13"
stamp "EXTRA DONE"
