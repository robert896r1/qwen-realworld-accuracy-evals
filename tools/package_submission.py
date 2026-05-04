#!/usr/bin/env python3
"""Package a validated run directory into a zip suitable for issue attachment."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sanitize(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).strip("-") or "submission"


def main() -> int:
    ap = argparse.ArgumentParser(description="Create a submission zip from a run directory.")
    ap.add_argument("run_dir")
    ap.add_argument("--out-dir", default="submissions/out")
    args = ap.parse_args()
    run_dir = Path(args.run_dir).resolve()
    validate = subprocess.run([sys.executable, str(ROOT / "tools" / "validate_run.py"), str(run_dir)], text=True)
    if validate.returncode != 0:
        return validate.returncode
    run = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    score = json.loads((run_dir / "score.json").read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    name = sanitize(f"{run.get('suite')}-{run.get('profile_label')}-{run.get('created_at')}.zip")
    zip_path = out_dir / name
    include = ["run.json", "score.json", "raw.jsonl", "notes.md", "environment.txt", "launch_command.txt"]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in include:
            zf.write(run_dir / name, arcname=name)
        raw_dir = run_dir / "raw_responses"
        if raw_dir.exists():
            for p in sorted(raw_dir.glob("*.json")):
                zf.write(p, arcname=f"raw_responses/{p.name}")
        checklist = "\n".join([
            "# Submission checklist",
            "",
            "- Confirm no secrets, proprietary code, customer data, or private repo content are included.",
            "- Confirm the launch command and hardware/runtime notes are accurate enough for reproduction.",
            "- Attach this zip to a `Submit run result` issue.",
            "",
            f"Score: {score.get('score')}/{score.get('score_total')} exact",
        ]) + "\n"
        zf.writestr("submission-checklist.md", checklist)
    print(f"Wrote submission package: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
