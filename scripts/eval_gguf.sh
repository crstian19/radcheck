#!/usr/bin/env bash
# Evaluate the v4 Q4_K_M GGUFs on the local AMD GPU with llama-server (bench + extra).
set -uo pipefail
cd ~/Dev/radcheck
mkdir -p outputs/eval-gguf
for n in radcheck-qwen35-4b-v4 radcheck-qwen35-9b-v4; do
  ~/Dev/llama.cpp/build/bin/llama-server -m models/$n/$n-Q4_K_M.gguf --jinja -ngl 99 -c 16384 -np 4 \
    --port 8080 > outputs/eval-gguf/$n-server.log 2>&1 &
  pid=$!
  until curl -sf localhost:8080/health >/dev/null; do sleep 2; done
  for d in "bench bench/radcheck_bench_v1_test.jsonl" "extra bench/radcheck_bench_v1_extra.jsonl"; do
    set -- $d
    start=$(date +%s)
    uv run --extra rocm python -m radcheck.evaluate --backend openai --model $n --data $2 \
      --system extended --concurrency 4 --out outputs/eval-gguf/$n-Q4_K_M-$1.json \
      > outputs/eval-gguf/$n-Q4_K_M-$1.log 2>&1
    echo "$n $1 $(( $(date +%s) - start )) s"
  done
  kill $pid; wait $pid 2>/dev/null
done
