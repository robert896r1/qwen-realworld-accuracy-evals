#!/usr/bin/env python3
import argparse, json, re, time, urllib.request, urllib.error
from datetime import datetime, timezone
from pathlib import Path

SYSTEM = "You are being evaluated for exact coding-agent accuracy. Return JSON only. No markdown fences. No prose. Do not include reasoning."

def post_json(url, api_key, payload, timeout):
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        'Content-Type':'application/json',
        'Authorization': f'Bearer {api_key}',
    })
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))

def strip_wrapper(text):
    return re.sub(r'^\s*<think>\s*</think>\s*', '', text or '', flags=re.I|re.S).strip()

def norm(v):
    if isinstance(v, str):
        return v.strip().lower()
    if isinstance(v, list):
        return [norm(x) for x in v]
    return v

def score_obj(got, expected):
    details = []
    ok = 0
    total = 0
    for k, exp in expected.items():
        total += 1
        if k not in got:
            details.append({'key':k,'ok':False,'expected':exp,'got':'<missing>'})
            continue
        gv = got[k]
        passed = norm(gv) == norm(exp)
        if passed: ok += 1
        details.append({'key':k,'ok':passed,'expected':exp,'got':gv})
    return ok, total, details

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--profile-label', required=True)
    ap.add_argument('--endpoint', required=True)
    ap.add_argument('--api-key', default='local')
    ap.add_argument('--timeout', type=int, default=240)
    ap.add_argument('--cases', default='cases.jsonl')
    ap.add_argument('--out-root', default='results')
    args = ap.parse_args()
    root = Path(__file__).resolve().parent
    cases = [json.loads(l) for l in (root / args.cases).read_text().splitlines() if l.strip()]
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = root / args.out_root / f'{stamp}-{args.profile_label}'
    out.mkdir(parents=True, exist_ok=True)
    recs = []
    for i, case in enumerate(cases, 1):
        print(f'[{i}/{len(cases)}] {case["id"]}', flush=True)
        payload = {
            'model': 'local',
            'messages': [
                {'role':'system','content':SYSTEM},
                {'role':'user','content':case['prompt']},
            ],
            'temperature': 0,
            'top_p': 1,
            'top_k': 1,
            'max_tokens': 700,
            'chat_template_kwargs': {'enable_thinking': False},
        }
        t0 = time.time(); response = None; content = ''; error = None; parsed = None
        try:
            response = post_json(args.endpoint, args.api_key, payload, args.timeout)
            content = (((response.get('choices') or [{}])[0].get('message') or {}).get('content') or '')
            stripped = strip_wrapper(content)
            parsed = json.loads(stripped)
            ok,total,details = score_obj(parsed, case['expected'])
        except Exception as e:
            error = repr(e)
            ok,total,details = 0, len(case['expected']), []
        elapsed = round(time.time()-t0, 3)
        rec = {
            'profile': args.profile_label,
            'case_id': case['id'],
            'category': case['category'],
            'min_ctx': case.get('min_ctx'),
            'weight': case.get('weight', 1.0),
            'elapsed_sec': elapsed,
            'error': error,
            'content': content,
            'parsed': parsed,
            'expected': case['expected'],
            'score': ok,
            'score_total': total,
            'weighted_score': ok * case.get('weight',1.0),
            'weighted_total': total * case.get('weight',1.0),
            'details': details,
            'raw_response_file': f'raw-{i:02d}-{case["id"]}.json' if response is not None else None,
        }
        recs.append(rec)
        if response is not None:
            (out / rec['raw_response_file']).write_text(json.dumps(response, indent=2), encoding='utf-8')
        with (out / 'results.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    summary = {
        'profile': args.profile_label,
        'cases': len(recs),
        'score': sum(r['score'] for r in recs),
        'score_total': sum(r['score_total'] for r in recs),
        'weighted_score': sum(r['weighted_score'] for r in recs),
        'weighted_total': sum(r['weighted_total'] for r in recs),
        'elapsed_sec': round(sum(r['elapsed_sec'] for r in recs), 3),
        'errors': sum(1 for r in recs if r['error']),
        'case_scores': [{k:r[k] for k in ['case_id','score','score_total','weighted_score','weighted_total','elapsed_sec','error']} for r in recs],
    }
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print('Wrote:', out)
    print(json.dumps(summary, indent=2))
if __name__ == '__main__':
    main()
