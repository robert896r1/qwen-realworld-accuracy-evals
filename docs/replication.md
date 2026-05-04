# Replication guide

## 1. Build or install llama.cpp

Use a recent `llama.cpp` with `llama-server` support for:

- OpenAI-compatible `/v1/chat/completions`;
- `--jinja`;
- `--reasoning`;
- `--reasoning-format`;
- `--chat-template-kwargs`;
- `--cache-type-k` and `--cache-type-v`.

## 2. Download models

Example Hugging Face CLI commands:

```bash
huggingface-cli download unsloth/Qwen3.6-27B-GGUF \
  --include 'Qwen3.6-27B-UD-Q6_K_XL.gguf' \
  --local-dir ~/models/qwen3.6-27b-unsloth

huggingface-cli download bartowski/Qwen_Qwen3.6-27B-GGUF \
  --include 'Qwen_Qwen3.6-27B-Q6_K_L.gguf' \
  --local-dir ~/models/qwen3.6-27b
```

## 3. Launch a profile

Use one of the scripts in `configs/` as a starting point. Example:

```bash
configs/launch-unsloth-128k-q8.sh
```

Adjust `llama-server` path and model paths as needed.

## 4. Run the exact suite

```bash
cd tests/max-accuracy-v1
./run_accuracy_eval.py \
  --profile-label my-profile-name \
  --endpoint http://127.0.0.1:8082/v1/chat/completions
```

## 5. Regenerate summaries and charts

From repo root:

```bash
scripts/generate_summary_and_charts.py
```

## 6. Compare

Review:

```text
results/max-accuracy-v1/summary.csv
charts/*.svg
```
