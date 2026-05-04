#!/usr/bin/env python3
"""Dependency-free validation for eval case JSONL files."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ID_RE = re.compile(r"^[a-z0-9][a-z0-9_\-]*$")
REQUIRED = ("id", "category", "prompt", "expected")


def validate_case(case: dict[str, Any], where: str) -> list[str]:
    errors = []
    for key in REQUIRED:
        if key not in case:
            errors.append(f"{where}: missing required key `{key}`")
    if "id" in case and not isinstance(case["id"], str):
        errors.append(f"{where}: `id` must be a string")
    elif "id" in case and not ID_RE.match(case["id"]):
        errors.append(f"{where}: `id` must match {ID_RE.pattern}")
    if "category" in case and not isinstance(case["category"], str):
        errors.append(f"{where}: `category` must be a string")
    if "prompt" in case and (not isinstance(case["prompt"], str) or not case["prompt"].strip()):
        errors.append(f"{where}: `prompt` must be a non-empty string")
    if "expected" in case and (not isinstance(case["expected"], dict) or not case["expected"]):
        errors.append(f"{where}: `expected` must be a non-empty object")
    if "weight" in case and not isinstance(case["weight"], (int, float)):
        errors.append(f"{where}: `weight` must be numeric")
    if "origin" in case and case["origin"] not in {"sanitized_real_world", "synthetic_reproduction", "control", "unknown"}:
        errors.append(f"{where}: `origin` must be sanitized_real_world, synthetic_reproduction, control, or unknown")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate eval cases JSONL.")
    ap.add_argument("path", nargs="?", default="evals/sidecar-companion-v1/cases.jsonl")
    args = ap.parse_args()
    path = Path(args.path)
    if not path.is_absolute():
        path = ROOT / path
    errors = []
    ids = set()
    count = 0
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            count += 1
            where = f"{path}:{line_no}"
            try:
                case = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{where}: invalid JSON: {e}")
                continue
            if not isinstance(case, dict):
                errors.append(f"{where}: case must be an object")
                continue
            errors.extend(validate_case(case, where))
            cid = case.get("id")
            if isinstance(cid, str):
                if cid in ids:
                    errors.append(f"{where}: duplicate id `{cid}`")
                ids.add(cid)
    if errors:
        print("Case validation failed:")
        for e in errors:
            print(f"- {e}")
        return 1
    print(f"Case validation OK: {count} cases in {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
