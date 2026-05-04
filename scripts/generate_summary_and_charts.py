#!/usr/bin/env python3
import csv
import json
from html import escape
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
    short = [r for r in recs if r['case_id'] not in ('needle_common_approx_35k', 'needle_extended_beyond_65k')]
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
    w.writeheader()
    w.writerows(profiles)


def svg_text(text: object) -> str:
    return escape(str(text), quote=False)


def svg_bar(filename, title, key, total_key=None, suffix='', max_value=None, note=None):
    width, height = 1100, 540 if note else 520
    margin_l, margin_r, margin_t, margin_b = 310, 40, 70, 110 if note else 90
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
    parts.append(f'<text x="{margin_l}" y="34" fill="#f8fafc" font-size="24" font-family="Inter, Arial" font-weight="700">{svg_text(title)}</text>')
    parts.append(f'<line x1="{margin_l}" y1="{margin_t + plot_h}" x2="{margin_l + plot_w}" y2="{margin_t + plot_h}" stroke="#334155"/>')
    for i, p in enumerate(profiles):
        y = margin_t + i * gap + (gap - bar_h) / 2
        val = vals[i]
        bw = 0 if maxv == 0 else plot_w * val / maxv
        color = '#38bdf8' if 'unsloth' in p['profile'] else '#a78bfa'
        if 'reasoning-on' in p['profile']:
            color = '#f59e0b'
        parts.append(f'<text x="20" y="{y + bar_h * 0.68:.1f}" fill="#cbd5e1" font-size="14" font-family="Inter, Arial">{svg_text(p["profile"])}</text>')
        parts.append(f'<rect x="{margin_l}" y="{y:.1f}" width="{bw:.1f}" height="{bar_h:.1f}" rx="7" fill="{color}"/>')
        label = f'{val:.1f}{suffix}' if isinstance(val, float) and not float(val).is_integer() else f'{int(val)}{suffix}'
        if total_key:
            label = f'{p[key]:.0f}/{p[total_key]:.0f} ({val:.1f}%)'
        if filename == 'elapsed-seconds.svg' and p['profile'] == 'unsloth-128k-f16':
            label = f'{label}*'
        parts.append(f'<text x="{margin_l + bw + 10:.1f}" y="{y + bar_h * 0.68:.1f}" fill="#f8fafc" font-size="14" font-family="Inter, Arial">{svg_text(label)}</text>')
    footer_y = height - 36 if note else height - 20
    parts.append(f'<text x="20" y="{footer_y}" fill="#94a3b8" font-size="13" font-family="Inter, Arial">Generated from results/max-accuracy-v1/summary.json</text>')
    if note:
        parts.append(f'<text x="20" y="{height - 16}" fill="#fbbf24" font-size="13" font-family="Inter, Arial">{svg_text(note)}</text>')
    parts.append('</svg>')
    (CHARTS / filename).write_text('\n'.join(parts), encoding='utf-8')


svg_bar('exact-score.svg', 'Exact-score accuracy by profile', 'score', 'score_total', max_value=100)
svg_bar('weighted-score.svg', 'Weighted accuracy by profile', 'weighted_score', 'weighted_total', max_value=100)
svg_bar(
    'elapsed-seconds.svg',
    'Elapsed seconds by profile',
    'elapsed_sec',
    suffix='s',
    note='* 128k f16 Unsloth hit local memory/throughput pressure and timed out on both long-context prompts.',
)

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

CASE_LABELS = {
    'arithmetic_constraint_control': ['arithmetic', 'constraint', 'control'],
    'routing_exact_control': ['routing', 'exact', 'control'],
    'python_patch_known_issues': ['python patch', 'known', 'issues'],
    'javascript_async_known_issues': ['javascript async', 'known', 'issues'],
    'operator_hard_directive': ['operator', 'hard', 'directive'],
    'ui_regression_exact': ['UI regression', 'exact'],
    'artifact_outlier_exact': ['artifact', 'outlier', 'exact'],
    'python_sorting_exact': ['python sorting', 'exact'],
    'needle_common_approx_35k': ['needle', '~35k', 'common'],
    'needle_extended_beyond_65k': ['needle', '>65k', 'extended'],
}

cell_w, cell_h = 108, 42
left, top = 235, 132
right, bottom = 35, 58
header_h = 78
width = left + cell_w * len(case_ids) + right
height = top + cell_h * len(profiles) + bottom
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<rect width="100%" height="100%" fill="#0b1020"/>',
]
parts.append(f'<text x="{left}" y="34" fill="#f8fafc" font-size="24" font-family="Inter, Arial" font-weight="700">Case pass heatmap</text>')
parts.append(f'<text x="{left}" y="58" fill="#94a3b8" font-size="13" font-family="Inter, Arial">Green = full credit, amber = partial, red = fail/error. Labels are wrapped on purpose so they stay readable on GitHub.</text>')
parts.append(f'<line x1="{left}" y1="{top - 12}" x2="{left + cell_w * len(case_ids) - 6}" y2="{top - 12}" stroke="#243044"/>')

for j, c in enumerate(case_ids):
    x = left + j * cell_w
    cx = x + (cell_w - 8) / 2
    label_lines = CASE_LABELS.get(c, c.replace('_', ' ').split())
    start_y = top - header_h + 20
    for li, line in enumerate(label_lines[:4]):
        parts.append(f'<text x="{cx:.1f}" y="{start_y + li * 14}" fill="#cbd5e1" font-size="11" font-family="Inter, Arial" text-anchor="middle">{svg_text(line)}</text>')

for i, p in enumerate(profiles):
    y = top + i * cell_h
    parts.append(f'<text x="18" y="{y + 26}" fill="#cbd5e1" font-size="13" font-family="Inter, Arial">{svg_text(p["profile"])}</text>')
    for j, c in enumerate(case_ids):
        score, total, err = case_scores[p['profile']][c]
        ratio = score / total if total else 0
        color = '#22c55e' if ratio == 1 else '#f59e0b' if ratio > 0 else '#ef4444'
        x = left + j * cell_w
        parts.append(f'<rect x="{x}" y="{y}" width="{cell_w - 8}" height="{cell_h - 7}" rx="6" fill="{color}" opacity="0.92"/>')
        parts.append(f'<text x="{x + (cell_w - 8) / 2}" y="{y + 22}" fill="#08111f" font-size="12" font-family="Inter, Arial" text-anchor="middle" font-weight="700">{score}/{total}</text>')
parts.append(f'<text x="18" y="{height - 22}" fill="#94a3b8" font-size="13" font-family="Inter, Arial">Generated from per-case records in results/max-accuracy-v1/raw/</text>')
parts.append('</svg>')
(CHARTS / 'case-heatmap.svg').write_text('\n'.join(parts), encoding='utf-8')
print(f'Wrote {OUT / "summary.csv"}, {OUT / "summary.json"}, charts/*.svg')
