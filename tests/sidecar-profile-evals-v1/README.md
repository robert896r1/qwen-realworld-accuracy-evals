# Local Qwen Profile Eval Test Pack v1

Purpose: compare local Bartowski/Unsloth Qwen profile quality for Robert's workflow:

- Codex challenge / validation
- bounded patch review
- frontend/UI design critique and verification
- governance / no-overbuild controls
- JSON/no-think compliance

This pack does **not** start or stop any model. Start exactly one profile with `startllm`, then run the eval against that endpoint.

## Cases

`cases.jsonl` contains 12 cases:

1. `monitor_mvp_scope_challenge`
2. `consensus_baseline_governance`
3. `cisco_source_metadata_plan`
4. `cisco_patch_review_synthetic`
5. `mls_outreach_ui_critique`
6. `design_translation_verification`
7. `json_parse_outlier_judgment`
8. `think_tag_false_positive_control`
9. `operator_intent_negative_control`
10. `short_logic_precision_control`
11. `short_schema_compliance_control`
12. `long_context_governance_attention`

## Bartowski f16 run

With Bartowski f16 running on port 8081:

```bash
cd ~/llm-consulting/profile-evals/test-pack-v1
./run_profile_eval.py \
  --profile-label bartowski-128k-f16 \
  --endpoint http://127.0.0.1:8081/v1/chat/completions
```

## Bartowski q8_0 run

Stop the current profile manually, then launch:

```bash
startllm 4
```

In another terminal:

```bash
cd ~/llm-consulting/profile-evals/test-pack-v1
./run_profile_eval.py \
  --profile-label bartowski-128k-q8 \
  --endpoint http://127.0.0.1:8081/v1/chat/completions
```

## Output

Results are written under:

```text
~/llm-consulting/profile-evals/test-pack-v1/results/<timestamp>-<profile-label>/
```

Files:

- `manifest.json` — endpoint/profile/server summary
- `results.jsonl` — per-case content and structural checks
- `summary.json` — compact structural summary
- `raw-XX-<case>.json` — raw OpenAI-compatible response per case

## Manual scoring

Use `rubric.md`. Structural checks are automatic; quality scoring remains human/Codex-reviewed because UI/design usefulness and challenge quality are not reliably machine-gradable.
