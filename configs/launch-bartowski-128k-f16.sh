#!/usr/bin/env bash
set -euo pipefail
llama-server \
  -m ~/models/qwen3.6-27b/Qwen_Qwen3.6-27B-Q6_K_L.gguf \
  --alias qwen-27b-q6k-nothink \
  --api-key local \
  --jinja \
  --reasoning off \
  --reasoning-format none \
  --chat-template-kwargs '{"enable_thinking":false}' \
  -ngl 999 -np 1 -c 131072 -n 8192 -fa on \
  --cache-type-k f16 --cache-type-v f16 \
  --temp 0.6 --top-k 20 --top-p 0.95 --min-p 0.0 \
  --repeat-penalty 1.0 --presence-penalty 0.0 --frequency-penalty 0.0 \
  --no-context-shift --host 127.0.0.1 --port 8081
