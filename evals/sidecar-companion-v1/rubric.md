# sidecar-companion-v1 rubric

The suite uses exact JSON-field scoring.

A case passes a field when the model returns the expected value for that exact key after simple normalization:

- strings are stripped and compared case-insensitively;
- lists are compared in order after normalizing each item;
- booleans and numbers must match exactly;
- missing keys fail;
- invalid JSON fails the full case.

The suite intentionally rewards boring, machine-checkable answers. It is not trying to grade prose quality.

## Why exact scoring

The repo is about whether a local model is useful as a sidecar in a real coding workflow. Exact scoring keeps the accepted suite reproducible and makes community run submissions comparable.

## Accepted case criteria

A new accepted case should be:

- derived from a real coding-agent failure mode or a faithful sanitized reproduction;
- small enough to run locally;
- safe to publish;
- deterministic enough to score;
- relevant to sidecar use: challenge, review, UI judgment, directive fidelity, artifact triage, or long-context verification.

A case should not be accepted only because it makes one model look good or bad.
