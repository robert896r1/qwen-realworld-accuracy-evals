# Qwen Real-World Accuracy Evals

This site documents a practical local evaluation of Qwen3.6 27B GGUF runtime profiles for coding-agent work.

The goal was to answer a narrow operator question:

> For a local Codex + Qwen workflow, which `llama.cpp` profile is the best real-world coding-agent sidecar configuration?

The evaluation focused on:

- exact coding and JavaScript/Python bug recognition;
- hard-directive/operator-intent fidelity;
- UI regression detection;
- artifact-quality judgment;
- long-context needle retrieval;
- KV cache format differences;
- 65k vs 128k context behavior;
- no-thinking vs a reasoning-flag variant.

## Charts

![Exact score](assets/charts/exact-score.svg)

![Weighted score](assets/charts/weighted-score.svg)

![Elapsed seconds](assets/charts/elapsed-seconds.svg)

![Case heatmap](assets/charts/case-heatmap.svg)

## Pages

- [Methodology](methodology.md)
- [Profiles](profiles.md)
- [Results](results.md)
- [Interpretation](interpretation.md)
- [Replication](replication.md)
