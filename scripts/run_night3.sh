#!/usr/bin/env bash
# Filler after run_night2.sh: fourth 9B seed (2 epochs) and a soup of four 9B seeds.
set -uo pipefail
cd ~/radcheck
export PATH="$HOME/.local/bin:$PATH"
stamp() { echo "=== $(date '+%F %T') $*"; }
mkdir -p outputs/eval-night2
ev() {  # ev <tag> <model> <adapter> <data> <system> [extra evaluate args]
  local tag=$1 model=$2 adapter=$3 data=$4 system=$5; shift 5
  stamp "eval $tag"
  uv run --extra cuda python -m radcheck.evaluate --backend hf --model "$model" --adapter "$adapter" \
    --data "$data" --system "$system" --batch-size 16 --out "outputs/eval-night2/$tag.json" "$@" \
    > "outputs/eval-night2/$tag.log" 2>&1 && stamp "done $tag" || stamp "FAILED $tag"
}
suite() {  # suite <tag> <model> <adapter>: the seven test sets
  local tag=$1 m=$2 a=$3
  ev "$tag-bench" "$m" "$a" data/bench_test.jsonl extended
  ev "$tag-extra" "$m" "$a" data/bench_extra.jsonl extended
  ev "$tag-pairs" "$m" "$a" data/robustness/pairs.jsonl extended
  ev "$tag-val" "$m" "$a" data/processed-v3/val.jsonl data
  ev "$tag-injector" "$m" "$a" data/processed-v3/test.jsonl data
  ev "$tag-noheaders" "$m" "$a" data/robustness/noheaders.jsonl extended
  ev "$tag-typos" "$m" "$a" data/robustness/typos.jsonl extended --max-new-tokens 768
}

stamp "waiting for run_night2.sh"
until grep -q "NIGHT2 DONE" outputs/night2-chain.log; do sleep 300; done

stamp "train qwen35-9b-v4-e2-s21"
uv run --extra cuda python -m radcheck.train --model Qwen/Qwen3.5-9B --data data/processed-v4 \
  --output outputs/train/qwen35-9b-v4-e2-s21 --epochs 2 --eval-steps 200 --max-length 3072 \
  --batch-size 4 --grad-accum 4 --seed 21 > outputs/train-qwen35-9b-v4-e2-s21.log 2>&1 \
  && { stamp "soup 9b x4"
       uv run --extra cuda python -m radcheck.soup --model Qwen/Qwen3.5-9B --adapters \
         outputs/train/qwen35-9b-v4-e2 outputs/train/qwen35-9b-v4-e2-s7 \
         outputs/train/qwen35-9b-v4-e2-s13 outputs/train/qwen35-9b-v4-e2-s21 \
         --out outputs/train/qwen35-9b-v4-soup4 > outputs/soup-9b4.log 2>&1 \
         && suite qwen35-9b-v4-soup4 Qwen/Qwen3.5-9B outputs/train/qwen35-9b-v4-soup4 \
         || stamp "FAILED soup 9b x4"; } \
  || stamp "FAILED train 9b s21"
stamp "NIGHT3 DONE"
