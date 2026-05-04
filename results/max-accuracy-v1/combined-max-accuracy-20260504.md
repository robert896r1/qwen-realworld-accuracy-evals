# Max accuracy profile comparison — updated with Unsloth 128k

Date: 2026-05-04

Scope: same exact-scored `max-accuracy-v1` suite across Bartowski and Unsloth profiles. VRAM is not used as a score criterion. The suite includes short exact code/instruction/UI checks, one common long-context needle, and one >65k context needle.

## Combined matrix

| Profile | Exact | Weighted | Errors | Elapsed | Short/code/UI exact | Common needle | Extended >65k needle | Result dir |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `unsloth-65k-f16` | 33/39 | 36/48 | 1 | 22.0s | 30/33 | 3/3 | 0/3 | `results/20260504T071349Z-unsloth-65k-f16` |
| `unsloth-65k-q8` | 33/39 | 36/48 | 1 | 23.7s | 30/33 | 3/3 | 0/3 | `results/20260504T071242Z-unsloth-65k-q8` |
| `bartowski-128k-f16` | 36/39 | 45/48 | 0 | 55.7s | 30/33 | 3/3 | 3/3 | `results/20260504T071456Z-bartowski-128k-f16` |
| `bartowski-128k-q8` | 36/39 | 45/48 | 0 | 56.7s | 30/33 | 3/3 | 3/3 | `results/20260504T071634Z-bartowski-128k-q8` |
| `unsloth-128k-f16` | 30/39 | 30/48 | 2 | 634.1s | 30/33 | 0/3 | 0/3 | `results/20260504T075708Z-unsloth-128k-f16` |
| `unsloth-128k-q8` | 36/39 | 45/48 | 0 | 57.6s | 30/33 | 3/3 | 3/3 | `results/20260504T080906Z-unsloth-128k-q8` |

## New Unsloth 128k launch confirmation

| Profile | Context | KV confirmation | Load notes |
|---|---:|---|---|
| `unsloth-128k-f16` | 131072 | K f16 4096 MiB + V f16 4096 MiB = 8192 MiB | offloaded 65/65 layers; log also reported `common_fit_params: failed to fit params to free device memory: n_gpu_layers already set by user to 999, abort`; long-context requests timed out |
| `unsloth-128k-q8` | 131072 | K q8_0 2176 MiB + V q8_0 2176 MiB = 4352 MiB | offloaded 65/65 layers; completed all cases |

## Readout

1. The 65k Unsloth profiles were not accuracy-competitive on the full suite only because they cannot accept the >65k test prompt. Inside their context envelope, they tied the others on the short/code/UI and common needle checks.

2. `unsloth-128k-q8` closed the gap completely: it tied `bartowski-128k-f16` and `bartowski-128k-q8` at 36/39 exact and 45/48 weighted.

3. `unsloth-128k-f16` is not a viable maximum-accuracy profile in this local runtime as tested. It did not produce wrong long-context answers; it failed to complete the two long-context cases before the client timeout, and its server timing was much slower than the q8 run.

4. The remaining 3 misses are common across the three successful 128k profiles:
   - enum/list exactness in `operator_hard_directive`,
   - marking `eval_candidate` false for the parse-warning artifact,
   - lexicographic sort order mismatch in `python_sorting_exact`.

## Recommendation

For maximum measured accuracy, the successful 128k profiles are tied:

- `bartowski-128k-f16`
- `bartowski-128k-q8`
- `unsloth-128k-q8`

If choosing between Unsloth profiles at 128k, use `unsloth-128k-q8`; `unsloth-128k-f16` timed out on both long-context cases.

If choosing a single overall profile from the evidence, use a 128k q8 profile. The exact-scored evidence did not show a quality loss from q8 KV, and q8 was the only Unsloth 128k variant that completed the full suite.
