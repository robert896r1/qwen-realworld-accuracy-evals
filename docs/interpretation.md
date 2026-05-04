# Interpretation

## What changed the outcome most

The strongest measured divider was **context window**, not f16 vs q8 KV.

- 65k profiles worked inside the 65k envelope.
- 65k profiles could not handle the >65k needle prompt.
- Successful 128k profiles passed both needle tests.

## q8 KV finding

The exact suite did not show an accuracy loss from q8 KV in the successful 128k profiles.

The following tied on the max-accuracy suite:

- `bartowski-128k-f16`
- `bartowski-128k-q8`
- `unsloth-128k-q8`
- `unsloth-128k-q8-reasoning-on-enable-false-preserve-false`

This does not prove q8 is universally equal to f16. It says no deficit appeared in this task-specific suite.

## Unsloth 128k f16 finding

`unsloth-128k-f16` loaded locally but timed out on both long-context cases. That profile was therefore not viable for this workflow as tested.

## Reasoning flag variant

The variant:

```bash
--reasoning on
--reasoning-format deepseek
--chat-template-kwargs '{"enable_thinking":false,"preserve_thinking":false}'
```

was accepted by `llama.cpp`, but produced the same score as the baseline Unsloth 128k q8 non-thinking profile. Raw responses did not expose a separate reasoning channel in the sampled outputs.

## Practical recommendation

For this workflow, the best tested operating tier is:

1. `unsloth-128k-q8`
2. `bartowski-128k-q8`
3. `bartowski-128k-f16`

This is not a claim that these are universally superior. It is the observed best set for Robert's local Codex + Qwen sidecar workflow.
