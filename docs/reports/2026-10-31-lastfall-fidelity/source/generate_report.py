#!/usr/bin/env python3
"""Render the complete Markdown review as Typst; no mathematical computation."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def clean(s):
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (\2)', s)
    return s.replace('**', '').replace('`', '').replace('*', '')

def text(s):
    return '#text(' + json.dumps(clean(s), ensure_ascii=False) + ')'

lines = (ROOT / 'report.md').read_text().splitlines()
out = ['#set page(paper: "a4", margin: 17mm, numbering: "1")',
       '#set text(font: "DejaVu Sans", size: 9pt)',
       '#set par(justify: false, leading: 0.55em)',
       '#set heading(numbering: none)',
       '#set table(inset: 4pt, stroke: 0.35pt + rgb("b9c8d8"))']
i = 0
while i < len(lines):
    s = lines[i]
    if not s:
        out.append('')
        i += 1
        continue
    if s.startswith('#'):
        level = len(s) - len(s.lstrip('#'))
        out.append('=' * level + ' ' + text(s[level:].strip()))
        if level == 1:
            out.append('#image("diagram.svg", width: 100%)')
        i += 1
    elif s.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            row = [v.strip() for v in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r'[: -]+', v) for v in row):
                rows.append(row)
            i += 1
        count = len(rows[0])
        widths = '(1fr,1.45fr,1fr,1.8fr)' if count == 4 else '(1.2fr,2fr,0.8fr,0.9fr,1fr)'
        out.append('#text(size: 7.5pt)[#table(columns: ' + widths + ',')
        for r, row in enumerate(rows):
            for cell in row:
                entry = text(cell)
                out.append(('table.cell(fill: rgb("e8eff7"))['+entry+']' if r == 0 else '['+entry+']')+',')
        out.append(')]')
    else:
        para = [s]
        i += 1
        while i < len(lines) and lines[i] and not lines[i].startswith(('#', '|', '- ')):
            para.append(lines[i])
            i += 1
        joined = ' '.join(para)
        if joined.startswith('- '):
            out.append('- ' + text(joined[2:]))
        else:
            out.append(text(joined))
(ROOT / 'report.typ').write_text('\n'.join(out) + '\n')
