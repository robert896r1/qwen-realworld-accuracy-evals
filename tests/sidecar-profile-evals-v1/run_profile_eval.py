#!/usr/bin/env python3
"""Run the local Qwen profile eval pack against an OpenAI-compatible llama.cpp endpoint.

This script does not start or stop models. Start the desired profile separately,
then run this script against the matching endpoint.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SYSTEM_PROMPT = """You are the local Qwen profile under evaluation for Robert's Codex-validation and frontend/UI workflow.
Follow the user's output schema exactly. Return final answer only. Do not include hidden reasoning, think tags, markdown fences, or prose outside the requested JSON.
Preserve operator intent, hard prohibitions, unresolved ambiguity, and human approval boundaries.
""".strip()


def load_cases(path: Path) -> list[dict]:
    cases = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as e:
                raise SystemExit(f"Invalid JSONL at {path}:{line_no}: {e}")
            cases.append(case)
    return cases


def resolve_prompt(case: dict, base_dir: Path) -> str:
    if "prompt_file" in case:
        return (base_dir / case["prompt_file"]).read_text(encoding="utf-8")
    return case["prompt"]


def post_json(url: str, api_key: str, payload: dict, timeout: int) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_json(url: str, api_key: str, timeout: int = 5) -> dict | None:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def structural_checks(text: str) -> dict:
    checks = {
        "json_valid": False,
        "think_tag_present": "<think" in text.lower() or "</think" in text.lower(),
        "markdown_fence_present": "```" in text,
    }
    try:
        json.loads(text)
        checks["json_valid"] = True
    except Exception:
        pass
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", default="cases.jsonl", help="Path to cases JSONL relative to pack dir or absolute")
    parser.add_argument("--pack-dir", default=Path(__file__).resolve().parent, type=Path)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8081/v1/chat/completions")
    parser.add_argument("--props-url", default=None, help="Optional /props URL; default inferred from endpoint")
    parser.add_argument("--api-key", default="local")
    parser.add_argument("--profile-label", required=True, help="Example: bartowski-128k-f16")
    parser.add_argument("--out-dir", default=None)
    parser.add_argument("--max-cases", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=float, default=0.8)
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()

    pack_dir = args.pack_dir.resolve()
    cases_path = Path(args.cases)
    if not cases_path.is_absolute():
        cases_path = pack_dir / cases_path
    cases = load_cases(cases_path)
    if args.max_cases:
        cases = cases[: args.max_cases]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.out_dir) if args.out_dir else pack_dir / "results" / f"{stamp}-{args.profile_label}"
    out_dir.mkdir(parents=True, exist_ok=True)

    props_url = args.props_url
    if props_url is None and "/v1/chat/completions" in args.endpoint:
        props_url = args.endpoint.replace("/v1/chat/completions", "/props")
    props = get_json(props_url, args.api_key) if props_url else None

    manifest = {
        "created_at": stamp,
        "profile_label": args.profile_label,
        "endpoint": args.endpoint,
        "props_url": props_url,
        "server_props_summary": None,
        "case_count": len(cases),
        "sampler": {"temperature": args.temperature, "top_p": args.top_p, "top_k": args.top_k},
    }
    if props:
        manifest["server_props_summary"] = {
            "model_alias": props.get("model_alias"),
            "model_path": props.get("model_path"),
            "build_info": props.get("build_info"),
            "n_ctx": (props.get("default_generation_settings") or {}).get("n_ctx"),
        }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    results_path = out_dir / "results.jsonl"
    summary = []
    with results_path.open("w", encoding="utf-8") as rf:
        for idx, case in enumerate(cases, 1):
            prompt = resolve_prompt(case, pack_dir)
            payload = {
                "model": props.get("model_alias") if props and props.get("model_alias") else "local-qwen-profile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": args.temperature,
                "top_p": args.top_p,
                "max_tokens": int(case.get("max_tokens", 900)),
                "extra_body": {
                    "top_k": args.top_k,
                    "chat_template_kwargs": {"enable_thinking": False},
                },
            }
            start = time.time()
            print(f"[{idx}/{len(cases)}] {case['id']}", flush=True)
            error = None
            response = None
            content = ""
            try:
                response = post_json(args.endpoint, args.api_key, payload, args.timeout)
                content = (((response.get("choices") or [{}])[0].get("message") or {}).get("content") or "")
            except (urllib.error.URLError, TimeoutError, Exception) as e:
                error = repr(e)
            elapsed = round(time.time() - start, 3)
            checks = structural_checks(content) if content else {"json_valid": False, "think_tag_present": False, "markdown_fence_present": False}
            rec = {
                "case_id": case["id"],
                "category": case["category"],
                "elapsed_sec": elapsed,
                "error": error,
                "content": content,
                "checks": checks,
                "expected_positive_signals": case.get("expected_positive_signals", []),
                "failure_modes": case.get("failure_modes", []),
                "raw_response_file": f"raw-{idx:02d}-{case['id']}.json" if response is not None else None,
            }
            if response is not None:
                (out_dir / rec["raw_response_file"]).write_text(json.dumps(response, indent=2), encoding="utf-8")
            rf.write(json.dumps(rec, ensure_ascii=False) + "\n")
            summary.append({"case_id": case["id"], "elapsed_sec": elapsed, "error": error, **checks})

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
