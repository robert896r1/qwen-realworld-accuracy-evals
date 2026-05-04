#!/usr/bin/env python3
"""Run an exact-scored sidecar eval suite against an existing OpenAI-compatible endpoint.

This tool never starts a model. Start your local server separately, then point this
script at its /v1 endpoint.
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SYSTEM = "You are being evaluated for exact coding-agent sidecar accuracy. Return JSON only. No markdown fences. No prose. Do not include reasoning."


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sanitize(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).strip("-") or "local-model"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"Invalid JSONL at {path}:{line_no}: {e}") from e
            for key in ("id", "category", "prompt", "expected"):
                if key not in case:
                    raise SystemExit(f"Case {path}:{line_no} missing required key: {key}")
            cases.append(case)
    return cases


def endpoint_from_base(base_url: str) -> str:
    base_url = base_url.rstrip("/")
    if base_url.endswith("/chat/completions"):
        return base_url
    return f"{base_url}/chat/completions"


def props_from_base(base_url: str | None, endpoint: str) -> str | None:
    if base_url:
        base = base_url.rstrip("/")
        if base.endswith("/v1"):
            return base[:-3] + "/props"
        if base.endswith("/chat/completions"):
            return base.removesuffix("/v1/chat/completions") + "/props"
    if "/v1/chat/completions" in endpoint:
        return endpoint.replace("/v1/chat/completions", "/props")
    return None


def post_json(url: str, api_key: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url: str | None, api_key: str, timeout: int = 5) -> dict[str, Any] | None:
    if not url:
        return None
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def strip_json_wrappers(text: str) -> str:
    text = (text or "").strip()
    text = re.sub(r"^\s*<think>\s*</think>\s*", "", text, flags=re.I | re.S).strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I).strip()
        text = re.sub(r"\s*```$", "", text).strip()
    return text


def norm(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().lower()
    if isinstance(value, list):
        return [norm(x) for x in value]
    return value


def score_obj(got: dict[str, Any], expected: dict[str, Any]) -> tuple[int, int, list[dict[str, Any]]]:
    ok = 0
    details = []
    for key, exp in expected.items():
        if key not in got:
            details.append({"key": key, "ok": False, "expected": exp, "got": "<missing>"})
            continue
        passed = norm(got[key]) == norm(exp)
        ok += int(passed)
        details.append({"key": key, "ok": passed, "expected": exp, "got": got[key]})
    return ok, len(expected), details


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def server_summary(props: dict[str, Any] | None) -> dict[str, Any] | None:
    if not props:
        return None
    default = props.get("default_generation_settings") or {}
    return {
        "model_alias": props.get("model_alias"),
        "model_path": props.get("model_path"),
        "build_info": props.get("build_info"),
        "n_ctx": default.get("n_ctx"),
        "n_predict": default.get("n_predict"),
    }


def write_text_artifacts(out: Path, args: argparse.Namespace, run_meta: dict[str, Any], score: dict[str, Any]) -> None:
    (out / "launch_command.txt").write_text(args.launch_command + "\n" if args.launch_command else "Not provided. The eval runner does not start models.\n", encoding="utf-8")
    env = {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "command": " ".join(sys.argv),
        "git_commit": run_meta.get("git_commit"),
        "server_props_summary": run_meta.get("server_props_summary"),
    }
    (out / "environment.txt").write_text(json.dumps(env, indent=2) + "\n", encoding="utf-8")
    notes = [
        f"# Run notes: {run_meta['profile_label']}",
        "",
        f"Suite: `{run_meta['suite']}`",
        f"Model: `{run_meta['model']}`",
        f"Score: {score['score']}/{score['score_total']} exact; {score['weighted_score']}/{score['weighted_total']} weighted",
        f"Elapsed: {score['elapsed_sec']}s",
        "",
        "This directory was generated by `tools/run_eval.py`. It is suitable for packaging with `tools/package_submission.py`.",
    ]
    if args.notes:
        notes += ["", "## Operator notes", "", args.notes]
    (out / "notes.md").write_text("\n".join(notes) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a sidecar eval suite against an existing OpenAI-compatible endpoint.")
    parser.add_argument("--suite", default="evals/sidecar-companion-v1", help="Suite directory containing suite.json and cases.jsonl")
    parser.add_argument("--base-url", default="http://127.0.0.1:8082/v1", help="OpenAI-compatible base URL, e.g. http://127.0.0.1:8082/v1")
    parser.add_argument("--endpoint", default=None, help="Full chat completions endpoint; overrides --base-url")
    parser.add_argument("--api-key", default="local")
    parser.add_argument("--model", default="local")
    parser.add_argument("--profile-label", default=None)
    parser.add_argument("--out", default=None, help="Output directory; default runs/local/<timestamp>-<profile>")
    parser.add_argument("--case-limit", type=int, default=None, help="Run only the first N cases for smoke testing")
    parser.add_argument("--case-id", action="append", default=None, help="Run a specific case id; may be repeated")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--props-url", default=None)
    parser.add_argument("--launch-command", default=None, help="Optional launch command text to capture in the run package")
    parser.add_argument("--notes", default=None)
    args = parser.parse_args()

    suite_dir = Path(args.suite)
    if not suite_dir.is_absolute():
        suite_dir = ROOT / suite_dir
    suite_meta = read_json(suite_dir / "suite.json") if (suite_dir / "suite.json").exists() else {"id": suite_dir.name}
    cases = load_cases(suite_dir / "cases.jsonl")
    if args.case_id:
        wanted = set(args.case_id)
        cases = [c for c in cases if c["id"] in wanted]
        missing = wanted - {c["id"] for c in cases}
        if missing:
            raise SystemExit(f"Unknown case id(s): {', '.join(sorted(missing))}")
    if args.case_limit:
        cases = cases[: args.case_limit]
    if not cases:
        raise SystemExit("No cases selected")

    endpoint = args.endpoint or endpoint_from_base(args.base_url)
    props_url = args.props_url or props_from_base(args.base_url, endpoint)
    props = get_json(props_url, args.api_key)
    profile_label = args.profile_label or sanitize(args.model)
    stamp = utc_stamp()
    out = Path(args.out) if args.out else ROOT / "runs" / "local" / f"{stamp}-{sanitize(profile_label)}"
    if not out.is_absolute():
        out = ROOT / out
    raw_dir = out / "raw_responses"
    raw_dir.mkdir(parents=True, exist_ok=True)

    run_meta = {
        "schema_version": "1.0",
        "suite": suite_meta.get("id", suite_dir.name),
        "suite_path": str(suite_dir.relative_to(ROOT) if suite_dir.is_relative_to(ROOT) else suite_dir),
        "created_at": stamp,
        "model": args.model,
        "profile_label": profile_label,
        "endpoint": endpoint,
        "props_url": props_url,
        "sampler": {"temperature": args.temperature, "top_p": args.top_p, "top_k": args.top_k, "max_tokens": args.max_tokens},
        "case_count": len(cases),
        "server_props_summary": server_summary(props),
        "git_commit": git_commit(),
    }
    (out / "run.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    recs = []
    raw_jsonl = out / "raw.jsonl"
    with raw_jsonl.open("w", encoding="utf-8") as f:
        for idx, case in enumerate(cases, 1):
            print(f"[{idx}/{len(cases)}] {case['id']}", flush=True)
            payload = {
                "model": args.model,
                "messages": [
                    {"role": "system", "content": DEFAULT_SYSTEM},
                    {"role": "user", "content": case["prompt"]},
                ],
                "temperature": args.temperature,
                "top_p": args.top_p,
                "top_k": args.top_k,
                "max_tokens": int(case.get("max_tokens", args.max_tokens)),
                "chat_template_kwargs": {"enable_thinking": False},
            }
            started = time.time()
            response = None
            content = ""
            parsed = None
            error = None
            try:
                response = post_json(endpoint, args.api_key, payload, args.timeout)
                content = (((response.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
                parsed = json.loads(strip_json_wrappers(content))
                score, total, details = score_obj(parsed, case["expected"])
            except Exception as e:
                error = repr(e)
                score, total, details = 0, len(case["expected"]), []
            elapsed = round(time.time() - started, 3)
            raw_file = None
            if response is not None:
                raw_file = f"raw-{idx:02d}-{case['id']}.json"
                (raw_dir / raw_file).write_text(json.dumps(response, indent=2), encoding="utf-8")
            rec = {
                "case_id": case["id"],
                "category": case["category"],
                "elapsed_sec": elapsed,
                "error": error,
                "content": content,
                "parsed": parsed,
                "expected": case["expected"],
                "score": score,
                "score_total": total,
                "weighted_score": score * case.get("weight", 1.0),
                "weighted_total": total * case.get("weight", 1.0),
                "details": details,
                "raw_response_file": f"raw_responses/{raw_file}" if raw_file else None,
            }
            recs.append(rec)
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    score = {
        "schema_version": "1.0",
        "suite": run_meta["suite"],
        "profile_label": profile_label,
        "cases": len(recs),
        "score": sum(r["score"] for r in recs),
        "score_total": sum(r["score_total"] for r in recs),
        "weighted_score": round(sum(r["weighted_score"] for r in recs), 3),
        "weighted_total": round(sum(r["weighted_total"] for r in recs), 3),
        "elapsed_sec": round(sum(r["elapsed_sec"] for r in recs), 3),
        "errors": sum(1 for r in recs if r["error"]),
        "case_scores": [{k: r[k] for k in ["case_id", "score", "score_total", "weighted_score", "weighted_total", "elapsed_sec", "error"]} for r in recs],
    }
    (out / "score.json").write_text(json.dumps(score, indent=2), encoding="utf-8")
    write_text_artifacts(out, args, run_meta, score)
    print(f"Wrote: {out}")
    print(json.dumps(score, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
