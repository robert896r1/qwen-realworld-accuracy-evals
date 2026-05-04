# Qwen Real-World Accuracy Evals

A reproducible local evaluation repo for Qwen3.6 27B GGUF profiles used as a real-world coding-agent sidecar: Codex challenger, validation assistant, UI/design reviewer, and long-context repo/session reviewer.

This is **not** a general-purpose LLM benchmark. It is a practical, operator-driven profile comparison for local `llama.cpp` workflows.

## Public/private status

This repository is intended to be reviewed privately first, then made public after final presentation approval.

## Quick links

- [Docs index](docs/index.md)
- [Methodology](docs/methodology.md)
- [Tested profiles and model links](docs/profiles.md)
- [Results](docs/results.md)
- [Interpretation](docs/interpretation.md)
- [Replication guide](docs/replication.md)

## Headline result

On the exact-scored max-accuracy suite, the best tested 128k profiles tied:

| Profile | Exact | Weighted |
|---|---:|---:|
| `bartowski-128k-f16` | 36/39 | 45/48 |
| `bartowski-128k-q8` | 36/39 | 45/48 |
| `unsloth-128k-q8` | 36/39 | 45/48 |

`unsloth-128k-f16` loaded but timed out on the two long-context cases in this local runtime. The 65k profiles worked inside their context envelope but failed the >65k case by construction.

## Hardware/runtime disclosure

- Hardware label supplied for publication: **NVIDIA RTX 3090 32GB**.
- Runtime: local `llama.cpp` server, OpenAI-compatible API.
- Raw model response JSON and scoring outputs are included.
- Server logs with local machine identifiers are not included in the public artifact; key KV/cache confirmations are summarized in the results docs.

## Attribution

Built from Robert's local Codex + Qwen sidecar workflow. Codex performed deterministic inspection, packaging, charting, and integration. Qwen was used as a local sidecar/challenger in the workflow being evaluated.

## License

MIT for scripts, docs, configs, and result packaging. Model weights are not included and remain under their upstream licenses.
