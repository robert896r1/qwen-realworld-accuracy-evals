---
layout: page
title: Contributing real-world cases and runs
---

The repo is useful only if it stays grounded in real work without becoming a dump of private prompts or random benchmark puzzles.

## The contribution model

There are two primary contribution types:

1. **Run results** against the canonical suite.
2. **Case proposals** derived from real coding-agent failure modes.

Both start as issues. Accepted suite changes are curated.

## Run results

Run results should be packaged with:

```bash
python tools/package_submission.py runs/local/<run-dir>
```

The zip includes:

- `run.json` — model/profile/runtime metadata;
- `score.json` — scored summary;
- `raw.jsonl` — per-case outputs and scores;
- `raw_responses/` — raw OpenAI-compatible responses;
- `environment.txt` — Python/platform/server props where available;
- `launch_command.txt` — launch command if supplied;
- `notes.md` — human-readable run notes.

Attach that zip to a **Submit run result** issue instead of committing local run output directly.

## Case proposals

A useful case proposal answers:

- What real workflow failure inspired this?
- What is the minimum safe context needed to reproduce it?
- What should the sidecar model return?
- How is it scored?
- Why does this matter when a local model is used beside Codex, Claude Code, Cursor, Aider, or another frontier coding agent?

## Accepted case rules

Accepted cases should test companion-agent usefulness:

- challenge quality;
- over-build detection;
- directive fidelity;
- frontend/UI judgment;
- artifact triage;
- code-review precision;
- long-context attention.

They should not be generic trivia or abstract puzzle prompts.

## Privacy rule

Describe the failure mode, not your business. Sanitize aggressively.
