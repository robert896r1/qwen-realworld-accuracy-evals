---
layout: page
title: Methodology
---

## What this evaluates

This evaluates local Qwen3.6 27B GGUF profiles as a **coding-agent sidecar**, not as a broad benchmark leaderboard.

The target workflow:

- Robert is the human operator and final decision-maker.
- Codex owns local inspection, patching, deterministic validation, and integration.
- Qwen is used as a local sidecar for challenge, validation, UI/design critique, and alternative reasoning.

## Suites

### `max-accuracy-v1`

Exact-scored JSON cases with known answers:

- arithmetic plus preserved constraints;
- route-selection exactness;
- Python patch review;
- TypeScript async bug detection;
- hard-directive compliance;
- UI regression detection;
- artifact parse-warning classification;
- Python sorting behavior;
- common long-context needle retrieval;
- extended >65k context needle retrieval.

This suite is intentionally strict: semantic near-misses can lose points if an exact enum/list/value is wrong.

### Historical qualitative sidecar pack

An earlier qualitative sidecar pack was used during local iteration, but it is not part of the public canonical suite. It was removed from the repo before broader release to keep the project focused on the reproducible exact-scored suite.

## Sampling and API shape

The exact suite sends OpenAI-compatible chat completions to `llama-server`, with fixed deterministic-ish request parameters in the runner:

```json
{
  "temperature": 0,
  "top_p": 1,
  "top_k": 1,
  "max_tokens": 700,
  "chat_template_kwargs": {"enable_thinking": false}
}
```

The server launch profile still matters: model file, context length, KV cache type, default sampling parameters, and reasoning/template settings are part of what was being evaluated.

## Limitations

- Single local machine and single-run profile samples.
- Synthetic but workflow-derived test cases.
- Exact scoring penalizes values that are semantically close but not exact.
- The suite is designed for a Codex + Qwen sidecar workflow, not for general reasoning leaderboard claims.
- Server logs with local device identifiers are not published; raw API outputs and scoring records are included.

## Canonical community suite

The contribution-facing suite is `evals/sidecar-companion-v1`. It uses exact JSON-field scoring so independent local runs can be compared without relying on subjective prose grading.

Historical test packs under `tests/` are kept for provenance. New contributors should start with `evals/sidecar-companion-v1` and the tools under `tools/`.
