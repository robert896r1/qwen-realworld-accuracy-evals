# Contributing

The goal is simple:

> Synthetic benchmarks tell you what a model can solve in isolation. This repo tests whether a local model is useful beside a frontier coding agent in real work.

Contributions are welcome, but the accepted suite stays curated. Easy to submit, hard to pollute.

## Contribution lanes

### 1. Replicate a run

If you have an OpenAI-compatible local endpoint running, run the canonical suite:

```bash
python tools/run_eval.py \
  --suite evals/sidecar-companion-v1 \
  --base-url http://127.0.0.1:8082/v1 \
  --model your-local-model-alias \
  --profile-label your-profile-label
```

For a quick smoke test:

```bash
python tools/run_eval.py \
  --suite evals/sidecar-companion-v1 \
  --base-url http://127.0.0.1:8082/v1 \
  --model your-local-model-alias \
  --profile-label smoke-test \
  --case-limit 2
```

Validate and package the result:

```bash
python tools/validate_run.py runs/local/<your-run-dir>
python tools/package_submission.py runs/local/<your-run-dir>
```

Attach the zip from `submissions/out/` to a **Submit run result** issue.

### 2. Propose a real-world eval case

The best cases are small sanitized reproductions of real coding-agent failures:

- the model over-built after being told not to;
- the model missed a UI regression;
- the model failed to challenge a bad Codex plan;
- the model hallucinated repo behavior;
- the model lost a long-context fact;
- the model gave plausible but wrong code-review output.

Open a **Propose real-world case** issue first. Do not PR random cases directly into the canonical suite.

A proposed case should include:

- the task prompt;
- the minimum context needed to reproduce the failure;
- the expected behavior;
- the scoring rule;
- the category being tested;
- privacy/sanitization notes;
- why the case matters for a local sidecar model.

Synthetic reproductions are welcome if they preserve the real failure mode.

### 3. Challenge a score

If a scoring rule is wrong or too brittle, open a **Scoring disagreement** issue with the case id, raw output, expected behavior, and proposed change.

## What not to submit

Do not submit:

- proprietary code;
- secrets, credentials, tokens, keys, internal URLs, or customer data;
- private repo content;
- prompt dumps with no expected answer;
- trivia;
- cases designed only to make one model look good or bad;
- vague subjective cases that cannot be scored.

## Quality bar

Good cases are boring to score and annoying for models to pass.

Accepted cases must be:

- safe to publish;
- reproducible;
- sidecar-relevant;
- deterministic enough to score;
- small enough for local users to run;
- useful beyond one person's machine.

## This repo does not provide models

This repo provides eval cases, scorers, result packaging, and documentation. It does not ship model weights or start model servers. Start your local model separately, then run the tools here against its OpenAI-compatible endpoint.
