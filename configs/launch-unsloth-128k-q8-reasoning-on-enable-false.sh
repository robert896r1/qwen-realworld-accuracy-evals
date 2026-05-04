#!/usr/bin/env bash
set -euo pipefail
llama-server \
  -m ~/models/qwen3.6-27b-unsloth/Qwen3.6-27B-UD-Q6_K_XL.gguf \
  --alias qwen-27b-unsloth-nothink \
  --api-key local \
  --jinja \
  --reasoning on \
  --reasoning-format deepseek \
  --chat-template-kwargs '{"enable_thinking":false,"preserve_thinking":false}' \
  -ngl 999 -np 1 -c 131072 -n 8192 -fa on \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --temp 0.7 --top-k 20 --top-p 0.80 --min-p 0.0 \
  --repeat-penalty 1.0 --presence-penalty 1.5 --frequency-penalty 0.0 \
  --no-context-shift --host 127.0.0.1 --port 8082
