#!/usr/bin/env python3
import csv, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'results' / 'max-accuracy-v1' / 'raw'
OUT = ROOT / 'results' / 'max-accuracy-v1'
CHARTS = ROOT / 'charts'
CHARTS.mkdir(exist_ok=True)

ORDER = [
    'unsloth-65k-f16',
    'unsloth-65k-q8',
    'bartowski-128k-f16',
    'bartowski-128k-q8',
    'unsloth-128k-f16',
    'unsloth-128k-q8',
    'unsloth-128k-q8-reasoning-on-enable-false-preserve-false',
]

profiles = []
for d in sorted(RAW.iterdir()):
    if not d.is_dir() or not (d / 'summary.json').exists():
        continue
    s = json.loads((d / 'summary.json').read_text())
    label = s['profile']
    if label not in ORDER:
        continue
    recs = [json.loads(l) for l in (d / 'results.jsonl').read_text().splitlines() if l.strip()]
    short = [r for r in recs if r['case_id'] not in ('needle_common_approx_35k','needle_extended_beyond_65k')]
    common = next(r for r in recs if r['case_id'] == 'needle_common_approx_35k')
    extended = next(r for r in recs if r['case_id'] == 'needle_extended_beyond_65k')
    profiles.append({
        'profile': label,
        'result_dir': str(d.relative_to(ROOT)),
        'score': s['score'],
        'score_total': s['score_total'],
        'weighted_score': s['weighted_score'],
        'weighted_total': s['weighted_total'],
        'accuracy_pct': round(100 * s['score'] / s['score_total'], 2),
        'weighted_pct': round(100 * s['weighted_score'] / s['weighted_total'], 2),
        'elapsed_sec': s['elapsed_sec'],
        'errors': s['errors'],
        'short_score': sum(r['score'] for r in short),
        'short_total': sum(r['score_total'] for r in short),
        'common_needle_score': common['score'],
        'common_needle_total': common['score_total'],
        'extended_needle_score': extended['score'],
        'extended_needle_total': extended['score_total'],
    })
profiles.sort(key=lambda x: ORDER.index(x['profile']))

(OUT / 'summary.json').write_text(json.dumps(profiles, indent=2), encoding='utf-8')
with (OUT / 'summary.csv').open('w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(profiles[0].keys()))
    w.writeheader(); w.writerows(profiles)

# Simple dependency-free SVG bar charts.
def svg_bar(filename, title, key, total_key=None, suffix='', max_value=None):
    width, height = 1100, 520
    margin_l, margin_r, margin_t, margin_b = 280, 40, 70, 90
    plot_w = width - margin_l - margin_r
    plot_h = height - margin_t - margin_b
    vals = []
    for p in profiles:
        if total_key:
            vals.append(100 * p[key] / p[total_key])
        else:
            vals.append(p[key])
    maxv = max_value if max_value is not None else max(vals) * 1.1
    bar_h = plot_h / len(profiles) * 0.62
    gap = plot_h / len(profiles)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">']
    parts.append('<rect width="100%" height="100%" fill="#0b1020"/>')
    parts.append(f'<text x="{margin_l}" y="34" fill="#f8fafc" font-size="24" font-family="Inter, Arial" font-weight="700">{title}</text>')
    # axis
    parts.append(f'<line x1="{margin_l}" y1="{margin_t+plot_h}" x2="{margin_l+plot_w}" y2="{margin_t+plot_h}" stroke="#334155"/>')
    for i, p in enumerate(profiles):
        y = margin_t + i*gap + (gap-bar_h)/2
        val = vals[i]
        bw = 0 if maxv == 0 else plot_w * val / maxv
        color = '#38bdf8' if 'unsloth' in p['profile'] else '#a78bfa'
        if 'reasoning-on' in p['profile']:
            color = '#f59e0b'
        parts.append(f'<text x="20" y="{y+bar_h*0.68:.1f}" fill="#cbd5e1" font-size="15" font-family="Inter, Arial">{p["profile"]}</text>')
        parts.append(f'<rect x="{margin_l}" y="{y:.1f}" width="{bw:.1f}" height="{bar_h:.1f}" rx="7" fill="{color}"/>')
        label = f'{val:.1f}{suffix}' if isinstance(val, float) and not float(val).is_integer() else f'{int(val)}{suffix}'
        if total_key:
            label = f'{p[key]:.0f}/{p[total_key]:.0f} ({val:.1f}%)'
        parts.append(f'<text x="{margin_l + bw + 10:.1f}" y="{y+bar_h*0.68:.1f}" fill="#f8fafc" font-size="14" font-family="Inter, Arial">{label}</text>')
    parts.append('<text x="20" y="500" fill="#94a3b8" font-size="13" font-family="Inter, Arial">Generated from results/max-accuracy-v1/summary.json</text>')
    parts.append('</svg>')
    (CHARTS / filename).write_text('\n'.join(parts), encoding='utf-8')

svg_bar('exact-score.svg', 'Exact-score accuracy by profile', 'score', 'score_total', max_value=100)
svg_bar('weighted-score.svg', 'Weighted accuracy by profile', 'weighted_score', 'weighted_total', max_value=100)
svg_bar('elapsed-seconds.svg', 'Elapsed seconds by profile', 'elapsed_sec', suffix='s')

# Heatmap by case for max accuracy suite.
case_ids = []
case_scores = {}
for p in profiles:
    d = ROOT / p['result_dir']
    rows = [json.loads(l) for l in (d / 'results.jsonl').read_text().splitlines() if l.strip()]
    case_scores[p['profile']] = {r['case_id']: (r['score'], r['score_total'], r['error']) for r in rows}
    for r in rows:
        if r['case_id'] not in case_ids:
            case_ids.append(r['case_id'])
cell_w, cell_h = 78, 32
left, top = 250, 90
width = left + cell_w*len(case_ids) + 40
height = top + cell_h*len(profiles) + 110
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="#0b1020"/>']
parts.append(f'<text x="{left}" y="34" fill="#f8fafc" font-size="24" font-family="Inter, Arial" font-weight="700">Case pass heatmap</text>')
for j,c in enumerate(case_ids):
    x = left + j*cell_w + cell_w/2
    parts.append(f'<text x="{x:.1f}" y="76" fill="#cbd5e1" font-size="11" font-family="Inter, Arial" text-anchor="middle" transform="rotate(-35 {x:.1f},76)">{c}</text>')
for i,p in enumerate(profiles):
    y = top + i*cell_h
    parts.append(f'<text x="15" y="{y+21}" fill="#cbd5e1" font-size="13" font-family="Inter, Arial">{p["profile"]}</text>')
    for j,c in enumerate(case_ids):
        score,total,err = case_scores[p['profile']][c]
        ratio = score/total if total else 0
        color = '#22c55e' if ratio == 1 else '#f59e0b' if ratio > 0 else '#ef4444'
        x = left + j*cell_w
        parts.append(f'<rect x="{x}" y="{y}" width="{cell_w-4}" height="{cell_h-4}" rx="5" fill="{color}" opacity="0.9"/>')
        parts.append(f'<text x="{x+cell_w/2-2}" y="{y+19}" fill="#08111f" font-size="12" font-family="Inter, Arial" text-anchor="middle" font-weight="700">{score}/{total}</text>')
parts.append('<text x="15" y="{}" fill="#94a3b8" font-size="13" font-family="Inter, Arial">Green = full credit, amber = partial, red = fail/error.</text>'.format(height-24))
parts.append('</svg>')
(CHARTS / 'case-heatmap.svg').write_text('\n'.join(parts), encoding='utf-8')
print(f'Wrote {OUT / "summary.csv"}, {OUT / "summary.json"}, charts/*.svg')
