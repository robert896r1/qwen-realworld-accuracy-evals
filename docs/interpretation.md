# Interpretation

The main readout is now on the repo front page. This page keeps the caveats in one place.

## What changed the outcome most

The biggest divider was **context window**, not f16 vs q8 KV.

- The 65k profiles worked inside the 65k envelope.
- The 65k profiles could not handle the >65k needle prompt.
- The successful 128k profiles passed both needle tests.

## q8 KV finding

This exact suite did not show an accuracy loss from q8 KV among the successful 128k profiles.

These tied:

- `bartowski-128k-f16`
- `bartowski-128k-q8`
- `unsloth-128k-q8`

That does **not** prove q8 is always equal to f16. It only says this task-specific suite did not expose a deficit.

## Unsloth 128k f16 finding

`unsloth-128k-f16` loaded locally, but the two long-context cases timed out. The useful wording is “not viable on this machine as configured,” not “answered incorrectly.”

## Practical recommendation

For Robert's local Codex + Qwen sidecar workflow, the best tested operating tier is:

1. `unsloth-128k-q8`
2. `bartowski-128k-q8`
3. `bartowski-128k-f16`

This is a workflow-specific result, not a universal model ranking.
