#!/usr/bin/env bash
# GGUF of the v4.1 soups (merge + Q8_0/Q4_K_M), then bench + extra on the local AMD GPU.
set -uo pipefail
cd ~/Dev/radcheck
mkdir -p outputs/eval-gguf
for spec in "4b Qwen/Qwen3.5-4B" "9b Qwen/Qwen3.5-9B"; do
  set -- $spec
  n=radcheck-qwen35-$1-v4.1
  echo "=== $(date '+%F %T') export $n"
  uv run --extra rocm python -m radcheck.export --model $2 --adapter outputs/train/qwen35-$1-v4-soup \
    --name $n > outputs/export-$n.log 2>&1 || { echo "FAILED export $n"; continue; }
  for q in Q8_0 Q4_K_M; do
    ~/Dev/llama.cpp/build/bin/llama-server -m models/$n/$n-$q.gguf --jinja -ngl 99 -c 16384 -np 4 \
      --port 8080 > outputs/eval-gguf/$n-$q-server.log 2>&1 &
    pid=$!
    until curl -sf localhost:8080/health >/dev/null; do sleep 2; done
    for d in "bench bench/radcheck_bench_v1_test.jsonl" "extra bench/radcheck_bench_v1_extra.jsonl"; do
      set -- $d
      uv run --extra rocm python -m radcheck.evaluate --backend openai --model $n --data $2 \
        --system extended --concurrency 4 --out outputs/eval-gguf/$n-$q-$1.json \
        > outputs/eval-gguf/$n-$q-$1.log 2>&1 && echo "done $n $q $1" || echo "FAILED $n $q $1"
    done
    kill $pid; wait $pid 2>/dev/null
  done
done
echo "=== $(date '+%F %T') SOUP GGUF DONE"
