# Qwen Real-World Accuracy Evals

These tests came out of a working Codex + local Qwen setup, not a leaderboard exercise.

In that workflow, Qwen has a narrow job: challenge Codex, catch over-building, review UI drafts, and stay useful when the prompt includes a lot of repo or session context. The question was practical: **which local `llama.cpp` profile is worth keeping on the desk?**

## Read this first

- The best 128k profiles tied on the scored suite: `bartowski-128k-f16`, `bartowski-128k-q8`, and `unsloth-128k-q8` all landed at **36/39 exact** and **45/48 weighted**.
- q8 KV did not show a measured accuracy loss in this suite. That is a local result, not a universal law.
- Context length mattered more than f16-vs-q8 KV. The 65k profiles handled the short and common-context cases, then failed the >65k needle by construction.
- `unsloth-128k-f16` loaded, but the long-context cases got stuck under local memory/throughput pressure and timed out. Treat that row as a local viability failure, not as evidence that the model gave bad long-context answers.

## Headline figures

Elapsed time shows the operational cost. The heatmap shows exactly where each profile broke.

![Elapsed seconds by profile](docs/assets/charts/elapsed-seconds.svg)

![Case pass heatmap](docs/assets/charts/case-heatmap.svg)

## Result table

| Profile | Exact | Weighted | Errors | Elapsed | Readout |
|---|---:|---:|---:|---:|---|
| `unsloth-65k-f16` | 33/39 | 36/48 | 1 | 22.0s | Good inside 65k; cannot take the >65k test. |
| `unsloth-65k-q8` | 33/39 | 36/48 | 1 | 23.7s | Same practical limit as the 65k f16 run. |
| `bartowski-128k-f16` | 36/39 | 45/48 | 0 | 55.7s | Tied for best measured accuracy. |
| `bartowski-128k-q8` | 36/39 | 45/48 | 0 | 56.7s | Tied for best measured accuracy; q8 KV did not hurt this suite. |
| `unsloth-128k-f16` | 30/39 | 30/48 | 2 | 634.1s* | Loaded, then timed out on both long-context cases. |
| `unsloth-128k-q8` | 36/39 | 45/48 | 0 | 57.6s | Tied for best measured accuracy and completed the full suite. |

\* The starred run loaded, but with 128k f16 KV it hit local memory/throughput pressure and timed out on both long-context prompts. The elapsed number includes timeout/cancellation behavior, so read it as “not viable on this machine as configured,” not as normal completed throughput.

## Practical take

For this workload, the keepers are:

1. `unsloth-128k-q8`
2. `bartowski-128k-q8`
3. `bartowski-128k-f16`

That order is deliberately conservative: prioritize the successful 128k q8 profiles for day-to-day local sidecar work, keep the Bartowski f16 result as the control, and do not read more into the data than this suite actually tested.

## Links

- [Methodology](docs/methodology.md)
- [Tested profiles and model links](docs/profiles.md)
- [Full results](docs/results.md)
- [Interpretation notes](docs/interpretation.md)
- [Replication guide](docs/replication.md)

## Hardware/runtime disclosure

- Hardware label supplied for publication: **NVIDIA RTX 3090 32GB**.
- Runtime: local `llama.cpp` server, OpenAI-compatible API.
- Raw model response JSON and scoring outputs are included.
- Server logs with local machine identifiers are not included in the public artifact; key KV/cache confirmations are summarized in the results docs.

## Attribution

Built from Robert's local Codex + Qwen sidecar workflow. Codex handled deterministic inspection, packaging, charting, and integration. Qwen was used as the local challenger in the workflow being evaluated.

## License

MIT for scripts, docs, configs, and result packaging. Model weights are not included and remain under their upstream licenses.
