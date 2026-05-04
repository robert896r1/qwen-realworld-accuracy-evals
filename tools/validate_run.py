#!/usr/bin/env python3
"""Dependency-free validation for a run directory created by tools/run_eval.py."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED_RUN = ("schema_version", "suite", "created_at", "model", "profile_label", "endpoint", "sampler", "case_count")
REQUIRED_SCORE = ("schema_version", "suite", "profile_label", "cases", "score", "score_total", "weighted_score", "weighted_total", "elapsed_sec", "errors")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a packaged eval run directory.")
    ap.add_argument("run_dir")
    args = ap.parse_args()
    run_dir = Path(args.run_dir).resolve()
    errors = []
    for name in ("run.json", "score.json", "raw.jsonl", "notes.md", "environment.txt", "launch_command.txt"):
        if not (run_dir / name).exists():
            errors.append(f"missing {name}")
    if errors:
        print("Run validation failed:")
        for e in errors:
            print(f"- {e}")
        return 1
    try:
        run = load_json(run_dir / "run.json")
        score = load_json(run_dir / "score.json")
    except Exception as e:
        print(f"Run validation failed: invalid JSON: {e}")
        return 1
    for key in REQUIRED_RUN:
        if key not in run:
            errors.append(f"run.json missing `{key}`")
    for key in REQUIRED_SCORE:
        if key not in score:
            errors.append(f"score.json missing `{key}`")
    raw_records = []
    with (run_dir / "raw.jsonl").open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"raw.jsonl:{line_no}: invalid JSON: {e}")
                continue
            raw_records.append(rec)
            raw_file = rec.get("raw_response_file")
            if raw_file and not (run_dir / raw_file).exists():
                errors.append(f"raw.jsonl:{line_no}: missing raw response file {raw_file}")
    if "case_count" in run and run["case_count"] != len(raw_records):
        errors.append(f"run.json case_count {run['case_count']} != raw.jsonl records {len(raw_records)}")
    if "cases" in score and score["cases"] != len(raw_records):
        errors.append(f"score.json cases {score['cases']} != raw.jsonl records {len(raw_records)}")
    if raw_records:
        summed = sum(int(r.get("score", 0)) for r in raw_records)
        total = sum(int(r.get("score_total", 0)) for r in raw_records)
        if score.get("score") != summed:
            errors.append(f"score.json score {score.get('score')} != raw summed score {summed}")
        if score.get("score_total") != total:
            errors.append(f"score.json score_total {score.get('score_total')} != raw summed total {total}")
    if errors:
        print("Run validation failed:")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"Run validation OK: {len(raw_records)} cases in {run_dir}")
    print(f"Score: {score['score']}/{score['score_total']} exact; elapsed {score['elapsed_sec']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
