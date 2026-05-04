# sidecar-companion-v1

This is the canonical exact-scored suite for the repo's current pitch:

> Synthetic benchmarks tell you what a model can solve in isolation. This suite tests whether a local model is useful beside a frontier coding agent in real work.

The cases are small on purpose. They target failure modes that matter when a local/open model is used as a sidecar reviewer, challenger, UI critic, or long-context sanity check for a paid/frontier coding agent.

## What this suite tests

- exact coding-agent judgment;
- operator directive fidelity;
- over-build / boundary detection;
- UI regression recognition;
- artifact triage;
- long-context retrieval;
- context envelope behavior.

## What this suite is not

It is not a general model leaderboard. It does not ship model weights, start model servers, or claim universal model quality.

## Files

- `suite.json` — suite metadata and version.
- `cases.jsonl` — canonical case definitions.
- `rubric.md` — scoring rules and acceptance notes.
