---
layout: page
title: Replication guide
---

This guide is written for someone who just found the repo and wants to test their own local model.

The repo does **not** provide model weights and does **not** launch a model server. You bring a local model runtime; this repo provides the eval cases, runner, scoring, and submission packaging.

## 1. Clone the repo

```bash
git clone https://github.com/robert896r1/qwen-realworld-accuracy-evals.git
cd qwen-realworld-accuracy-evals
```

## 2. Start your local model

Start your model using your own runtime: `llama.cpp`, Ollama, vLLM, LM Studio, or anything else that exposes an OpenAI-compatible endpoint.

The runner expects this kind of endpoint:

```text
http://127.0.0.1:<port>/v1/chat/completions
```

If your base URL is:

```text
http://127.0.0.1:8082/v1
```

then pass:

```bash
--base-url http://127.0.0.1:8082/v1
```

Reference `llama.cpp` launch examples from the original tests live here:

```text
examples/launch/llama-cpp/
```

Those scripts are examples only. Adjust model paths, ports, context size, KV cache, and runtime flags for your machine.

## 3. Run a two-case smoke test

Do this before running the full suite. It confirms that your endpoint, auth, JSON parsing, scoring, and output folder all work.

```bash
python tools/run_eval.py \
  --base-url http://127.0.0.1:8082/v1 \
  --profile-label my-local-smoke-test \
  --case-limit 2
```

Important distinction:

- `--base-url` points to the model server that is already running.
- `--profile-label` names the output folder and result package.
- `--profile-label` does not change the model being tested.
- `--model` defaults to `local`; only set it if your server requires a specific model name.

If your server does require a model name:

```bash
python tools/run_eval.py \
  --base-url http://127.0.0.1:8082/v1 \
  --model local \
  --profile-label qwen3.6-27b-unsloth-128k-q8-smoke \
  --case-limit 2
```

Expected output:

- a new directory under `runs/local/`;
- `run.json` with model/runtime metadata;
- `raw.jsonl` with per-case outputs;
- `score.json` with exact score summary;
- `notes.md`, `environment.txt`, and `launch_command.txt`.

Validate the newest run:

```bash
RUN_DIR="$(ls -td runs/local/* | head -1)"
python tools/validate_run.py "$RUN_DIR"
```

## 4. Run the full canonical suite

Once the smoke test works, run the full suite by removing `--case-limit`:

```bash
python tools/run_eval.py \
  --base-url http://127.0.0.1:8082/v1 \
  --profile-label qwen3.6-27b-unsloth-128k-q8
```

## 5. Package a shareable submission

```bash
RUN_DIR="$(ls -td runs/local/* | head -1)"
python tools/validate_run.py "$RUN_DIR"
python tools/package_submission.py "$RUN_DIR"
```

The zip lands in:

```text
submissions/out/
```

Attach that zip to a **Submit run result** issue. Do not commit local run output directly.

## 6. Regenerate existing summary charts

The published charts are generated from the historical result set already committed under `results/max-accuracy-v1/raw/`:

```bash
python scripts/generate_summary_and_charts.py
cp charts/*.svg docs/assets/charts/
```

That chart script is for the current published result matrix. New community run packages should stay out of the canonical chart until reviewed.
