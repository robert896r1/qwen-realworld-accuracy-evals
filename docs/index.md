# Qwen Real-World Accuracy Evals

These tests came from a working Codex + local Qwen workflow. Qwen's job there is not to replace Codex; it is the second set of eyes for challenge, validation, UI review, and long-context sanity checks.

The practical question was: **which local `llama.cpp` profile should stay in rotation?**

## Short answer

- `bartowski-128k-f16`, `bartowski-128k-q8`, and `unsloth-128k-q8` tied at **36/39 exact** and **45/48 weighted**.
- q8 KV showed no measured accuracy loss in this suite.
- 65k context was the wrong envelope for the full workload because it could not take the >65k needle case.
- `unsloth-128k-f16` loaded, but the long-context requests timed out under local memory/throughput pressure.

## Headline figures

![Elapsed seconds](assets/charts/elapsed-seconds.svg)

![Case heatmap](assets/charts/case-heatmap.svg)

## Result table

| Profile | Exact | Weighted | Errors | Elapsed |
|---|---:|---:|---:|---:|
| `unsloth-65k-f16` | 33/39 | 36/48 | 1 | 22.0s |
| `unsloth-65k-q8` | 33/39 | 36/48 | 1 | 23.7s |
| `bartowski-128k-f16` | 36/39 | 45/48 | 0 | 55.7s |
| `bartowski-128k-q8` | 36/39 | 45/48 | 0 | 56.7s |
| `unsloth-128k-f16` | 30/39 | 30/48 | 2 | 634.1s* |
| `unsloth-128k-q8` | 36/39 | 45/48 | 0 | 57.6s |

\* Loaded, then timed out on both long-context prompts under local memory/throughput pressure. The elapsed value includes those timeouts.

## Pages

- [Methodology](methodology.md)
- [Profiles and model links](profiles.md)
- [Results](results.md)
- [Interpretation](interpretation.md)
- [Replication](replication.md)
- [Contributing cases](contributing-cases.md)
