#!/usr/bin/env bash
# Night queue (1-2 nov), only the 4B and 9B (the target sizes). Starts after run_extra.sh:
# 1) 9B soup of three seeds; 2) typos test again with room for long answers (the "invalid
# JSON" there was truncation after many transcripcion flags); 3) reasoning distillation with
# rejection sampling (v4d: the 27B never sees the answer); 4) two more 4B seeds and a soup of 5.
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
suite() {  # suite <tag> <model> <adapter> [extra]: the seven test sets
  local tag=$1 m=$2 a=$3; shift 3
  ev "$tag-bench" "$m" "$a" data/bench_test.jsonl extended "$@"
  ev "$tag-extra" "$m" "$a" data/bench_extra.jsonl extended "$@"
  ev "$tag-pairs" "$m" "$a" data/robustness/pairs.jsonl extended "$@"
  ev "$tag-val" "$m" "$a" data/processed-v3/val.jsonl data "$@"
  ev "$tag-injector" "$m" "$a" data/processed-v3/test.jsonl data "$@"
  ev "$tag-noheaders" "$m" "$a" data/robustness/noheaders.jsonl extended "$@"
  ev "$tag-typos" "$m" "$a" data/robustness/typos.jsonl extended --max-new-tokens 768 "$@"
}
train() {  # train <tag> <model> [extra train args]
  local tag=$1 model=$2; shift 2
  stamp "train $tag"
  uv run --extra cuda python -m radcheck.train --model "$model" --output "outputs/train/$tag" \
    --epochs 2 --eval-steps 200 --max-length 3072 --batch-size 4 --grad-accum 4 "$@" \
    > "outputs/train-$tag.log" 2>&1
}

stamp "waiting for run_extra.sh"
until grep -q "EXTRA DONE" outputs/extra-chain.log; do sleep 300; done

# 1. 9B soup of three seeds (42, 7, 13).
stamp "soup 9b x3"
uv run --extra cuda python -m radcheck.soup --model Qwen/Qwen3.5-9B --adapters \
  outputs/train/qwen35-9b-v4-e2 outputs/train/qwen35-9b-v4-e2-s7 outputs/train/qwen35-9b-v4-e2-s13 \
  --out outputs/train/qwen35-9b-v4-soup3 > outputs/soup-9b3.log 2>&1 \
  && suite qwen35-9b-v4-soup3 Qwen/Qwen3.5-9B outputs/train/qwen35-9b-v4-soup3 \
  || stamp "FAILED soup 9b x3"

# 2. Typos with room for long answers, for the published v4.1 soups.
ev qwen35-4b-v4-soup-typos768 Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v4-soup \
  data/robustness/typos.jsonl extended --max-new-tokens 768
ev qwen35-9b-v4-soup-typos768 Qwen/Qwen3.5-9B outputs/train/qwen35-9b-v4-soup \
  data/robustness/typos.jsonl extended --max-new-tokens 768

# 3. Distillation with rejection sampling, then the 4B on the kept examples.
stamp "distill"
PYTHONPATH=src ~/radcheck-vllm/bin/python -m radcheck.distill --data data/processed-v4 \
  --out data/processed-v4d > outputs/distill.log 2>&1 \
  && { stamp "done distill: $(tr -d '\n ' < data/processed-v4d/stats.json)"
       train qwen35-4b-v4d Qwen/Qwen3.5-4B --data data/processed-v4d --no-grad-checkpointing \
         && suite qwen35-4b-v4d Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v4d --max-new-tokens 768 \
         || stamp "FAILED train v4d"; } \
  || stamp "FAILED distill"

# 4. Two more 4B seeds and a soup of five.
for s in 21 99; do
  train qwen35-4b-v4-s$s Qwen/Qwen3.5-4B --data data/processed-v4 --no-grad-checkpointing \
    --seed $s || stamp "FAILED train 4b s$s"
done
stamp "soup 4b x5"
uv run --extra cuda python -m radcheck.soup --model Qwen/Qwen3.5-4B --adapters \
  outputs/train/qwen35-4b-v4 outputs/train/qwen35-4b-v4-s7 outputs/train/qwen35-4b-v4-s13 \
  outputs/train/qwen35-4b-v4-s21 outputs/train/qwen35-4b-v4-s99 \
  --out outputs/train/qwen35-4b-v4-soup5 > outputs/soup-4b5.log 2>&1 \
  && suite qwen35-4b-v4-soup5 Qwen/Qwen3.5-4B outputs/train/qwen35-4b-v4-soup5 \
  || stamp "FAILED soup 4b x5"
stamp "NIGHT2 DONE"
