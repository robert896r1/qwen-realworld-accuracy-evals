# Bartowski 128k KV profile eval — 2026-05-03

Scope: compare Bartowski `Qwen_Qwen3.6-27B-Q6_K_L.gguf` at 128k context with explicit KV cache settings:

- `bartowski-128k-f16`: `--cache-type-k f16 --cache-type-v f16`
- `bartowski-128k-q8`: `--cache-type-k q8_0 --cache-type-v q8_0`

Both used no-think launch mode and the same test pack at `llm-consulting/profile-evals/test-pack-v1`.

## Launch/log confirmation

| Profile | Result dir | Server log KV confirmation |
|---|---|---|
| `bartowski-128k-f16` | `results/20260503T210821Z-bartowski-128k-f16` | `K (f16): 4096.00 MiB, V (f16): 4096.00 MiB`; total KV `8192.00 MiB` |
| `bartowski-128k-q8` | `results/20260503T214649Z-bartowski-128k-q8` | `K (q8_0): 2176.00 MiB, V (q8_0): 2176.00 MiB`; total KV `4352.00 MiB` |

q8 KV saved 3840 MiB of KV cache allocation versus f16 at the same 131072 context.

## Structural results

Strict parser means the raw assistant `content` must parse as JSON with no preamble.

| Metric | f16 KV | q8_0 KV |
|---|---:|---:|
| Cases run | 12 | 12 |
| Raw strict JSON valid | 0/12 | 0/12 |
| Empty `<think></think>` preamble present | 12/12 | 12/12 |
| JSON valid after stripping only the empty preamble | 9/12 | 10/12 |
| Markdown fence violations | 0/12 | 0/12 |
| Runner/API errors | 0/12 | 0/12 |
| Wall elapsed | 91.113s | 83.405s |
| Prompt tokens | 18,393 | 18,393 |
| Completion tokens | 4,514 | 3,980 |

The empty `<think>\n\n</think>` prefix comes from the Qwen chat template when `enable_thinking` is false; it is not substantive hidden reasoning, but it still breaks strict JSON consumers unless stripped or avoided.

## Case-level qualitative notes

| Case | f16 KV | q8_0 KV | Read |
|---|---|---|---|
| `monitor_mvp_scope_challenge` | Strong | Strong | Both rejected overbuilt active enforcement, preserved UI requirement, reduced rating friction. q8 was slightly tighter. |
| `consensus_baseline_governance` | Strong | Strong | Both rejected model consensus as approval and preserved Robert approval. q8 explicitly named collusive error and AGENTS.md approval boundary. |
| `cisco_source_metadata_plan` | Strong | Strong | Both caught missing metadata fallback, smoke-test overfitting, soft-evidence risk, content payload/latency. |
| `cisco_patch_review_synthetic` | Medium | Strong | f16 caught mutation and missing title but emitted invalid JSON due unescaped `""`; q8 emitted valid JSON and caught mutation, missing title, placeholder/undefined result issue. Neither clearly handled trace payload bloat as a first-class issue. |
| `mls_outreach_ui_critique` | Strong | Strong | Both gave useful front-end critique: primary CTA hierarchy, cognitive load, redundant metrics, progressive disclosure, workflow mechanics. |
| `design_translation_verification` | Strong | Strong | Both rejected broken controls/design drift and required UI interaction/visual tests. |
| `json_parse_outlier_judgment` | Medium | Strong | Both preserved substantive raw response despite schema failure. q8 typed fields more cleanly; f16 used string booleans/numeric rating. |
| `think_tag_false_positive_control` | Medium | Medium | Both correctly classified literal tag discussion as safe, but both emitted invalid JSON by placing a literal newline-containing `</think>` string unescaped. |
| `operator_intent_negative_control` | Strong | Strong | Both enforced the hard directive and bounded stop behavior. |
| `short_logic_precision_control` | Fail | Fail | Both answered `42` while their own calculation self-corrected to `14`; this is a material arithmetic/answer consistency failure. |
| `short_schema_compliance_control` | Strong | Medium | f16 routed to `qwen`; q8 routed to `@qwen`, which is semantically understandable but not exact expected value. |
| `long_context_governance_attention` | Strong | Strong | Both preserved late governance constraints and did not claim true continuous co-presence. |

## Ratings for this use case

These are local, pack-specific ratings for Codex challenge/validation and front-end UI design support, not general model benchmarks.

| Dimension | f16 KV | q8_0 KV |
|---|---:|---:|
| Challenge signal | 8.0/10 | 8.2/10 |
| Correctness / low hallucination | 6.8/10 | 7.2/10 |
| Operator-intent fidelity | 8.0/10 | 7.8/10 |
| UI/design critique usefulness | 8.0/10 | 8.0/10 |
| Machine-output compliance | 3.0/10 | 3.5/10 |
| Operational fit on 32GB VRAM | 6.5/10 | 8.5/10 |
| Overall for current workflow | 7.0/10 | 7.5/10 |

## Bottom line

Within this test pack, q8_0 KV is the better Bartowski operating profile for the current 128k operator/harness workflow because it preserved substantially the same qualitative challenge/design behavior while saving about 3.75 GiB of KV memory. The quality gap did not favor f16 KV in this run.

Major caveat: both profiles currently emit the empty no-think preamble in assistant content, and both failed the short arithmetic control. For strict automated harness use, response normalization or a template/launch adjustment is needed before treating either profile as clean JSON output.
