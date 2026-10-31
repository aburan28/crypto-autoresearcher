#!/usr/bin/env python3
"""Render the frozen source-scope inventory as an SVG evidence diagram."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
m = json.loads((ROOT / 'manifest.json').read_text())
counts = {name: m['snapshots'][name]['tracked_lean_files']
          for name in ('crypto', 'cryptanalysis', 'auto-researcher')}
b = m['cryptanalysis_corpus_boundary']
parts = [('Archived-identical in receipt', len(b['archived_byte_identical_paths']), '#2563a6'),
         ('Fresh native in receipt', len(b['fresh_native_receipt_paths']), '#25866b'),
         ('Outside this receipt', len(b['outside_this_receipt_paths']), '#d7872e')]
assert counts == {'crypto': 474, 'cryptanalysis': 184, 'auto-researcher': 363}
assert sum(n for _, n, _ in parts) == counts['cryptanalysis']

out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="750" viewBox="0 0 1100 750">',
       '<rect width="1100" height="750" fill="#fffdf8"/>',
       '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#172b43} .title{font-size:29px;font-weight:700} .subtitle{font-size:17px} .label{font-size:18px} .small{font-size:14px} .count{font-size:20px;font-weight:700} .section{font-size:22px;font-weight:700}</style>']
def text(x, y, value, cls='label'):
    out.append(f'<text x="{x}" y="{y}" class="{cls}">{html.escape(str(value))}</text>')
def rect(x, y, w, h, fill):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="5" fill="{fill}"/>')

text(55, 55, 'Lean source-tree scope at frozen Git commits', 'title')
text(55, 85, 'Tracked .lean files; file counts are not theorem or claim coverage.', 'subtitle')
text(55, 128, 'All tracked Lean files by repository', 'section')
for y, name, color in [(163, 'crypto', '#2e5c89'), (228, 'cryptanalysis', '#547b9e'),
                       (293, 'auto-researcher', '#7196af')]:
    text(55, y + 29, name)
    rect(270, y, 665 * counts[name] / 500, 42, color)
    text(955, y + 29, counts[name], 'count')
text(55, 374, 'Cryptanalysis: membership in the 97-source corpus receipt', 'section')
text(55, 401, 'Partition of 184 tracked Lean files at d3673ee; membership is not a validity verdict.', 'small')
x = 55
for label, count, color in parts:
    width = 920 * count / 184
    rect(x, 426, width, 46, color)
    x += width
for y, (label, count, color) in zip((510, 540, 570), parts):
    rect(58, y - 16, 22, 18, color)
    text(92, y, f'{count}  {label}', 'label')
text(55, 617, 'The 87 files outside this receipt may have other gates; inspect each claim and its source.', 'small')
text(55, 641, 'The receipt binds 90 unchanged archive files and seven fresh native files. It leaves', 'small')
text(55, 661, 'exhaustive theorem audit, semantic fidelity, and historical execution open.', 'small')
text(55, 700, 'Sources: crypto 192e5eec; cryptanalysis d3673ee; auto researcher 7a40243d.', 'small')
text(55, 723, 'Exact trees, file paths, Git blob IDs, and receipt partition are in manifest.json and inventories.', 'small')
out.append('</svg>')
(ROOT / 'scope.svg').write_text('\n'.join(out) + '\n')
print('wrote scope.svg')
