# Profile Eval Rubric v1

Use this rubric to compare Bartowski KV profiles for Codex validation/challenge/frontend UI work.

Score each case 1-5:

| Dimension | Weight | Signals |
| --- | ---: | --- |
| Challenge signal | 25% | Catches overbuild, weak assumptions, bad governance, missing validation. |
| Correctness / low hallucination | 20% | Does not invent facts, separates blockers from preferences, catches real bugs. |
| Operator intent fidelity | 20% | Preserves hard directives, approval boundaries, unresolved ambiguity. |
| UI/design usefulness | 15% | Product-specific hierarchy/layout/workflow guidance, not generic styling. |
| Output compliance | 10% | JSON valid, no markdown fences, no think-tag leakage, follows schema. |
| Operational fit | 10% | Latency, errors, stability, usable output length. |

Suggested profile verdicts:

- 4.5-5.0: default validator/challenger
- 4.0-4.49: strong, use if more stable/faster
- 3.0-3.99: acceptable fallback
- 2.0-2.99: constrained use only
- <2.0: do not use for Codex validation

Important: expected_positive_signals and failure_modes in `cases.jsonl` are evaluator guidance only. They must not be sent to the model.
