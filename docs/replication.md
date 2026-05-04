# Replication guide

The fastest path assumes you already have a local OpenAI-compatible endpoint running. This repo does not download models or start model servers.

## 1. Clone the repo

```bash
git clone https://github.com/robert896r1/qwen-realworld-accuracy-evals.git
cd qwen-realworld-accuracy-evals
```

## 2. Start your model separately

Use your own runtime. The original tests used local `llama.cpp` servers. Reference launch examples live under:

```text
examples/launch/llama-cpp/
```

Those scripts are examples only. Adjust paths, ports, context size, KV cache, and runtime flags for your machine.

## 3. Smoke-test the runner

Run two short cases first:

```bash
python tools/run_eval.py \
  --suite evals/sidecar-companion-v1 \
  --base-url http://127.0.0.1:8082/v1 \
  --model your-local-model-alias \
  --profile-label smoke-test \
  --case-limit 2
```

Expected output:

- a new directory under `runs/local/`;
- `run.json` with model/runtime metadata;
- `raw.jsonl` with per-case outputs;
- `score.json` with exact score summary;
- `notes.md`, `environment.txt`, and `launch_command.txt`.

Validate it:

```bash
python tools/validate_run.py runs/local/<run-dir>
```

## 4. Run the full canonical suite

```bash
python tools/run_eval.py \
  --suite evals/sidecar-companion-v1 \
  --base-url http://127.0.0.1:8082/v1 \
  --model your-local-model-alias \
  --profile-label your-profile-label
```

## 5. Package a submission

```bash
python tools/package_submission.py runs/local/<run-dir>
```

Attach the zip from `submissions/out/` to a **Submit run result** issue. Do not commit local run output directly.

## 6. Regenerate existing summary charts

The published charts are generated from the historical result set already committed under `results/max-accuracy-v1/raw/`:

```bash
python scripts/generate_summary_and_charts.py
cp charts/*.svg docs/assets/charts/
```

That chart script is for the current published result matrix. New community run packages should stay out of the canonical chart until reviewed.
