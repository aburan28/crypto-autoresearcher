from pathlib import Path
import hashlib
import json

import typst


study = Path('analysis/semaev-degree-five-quotient-lift')
source = study / 'validation/panel-coverage-20261031-001/coverage.json'
report = study / 'reports/panel-coverage-20261031-001'
report.mkdir(parents=True, exist_ok=True)
data = json.loads(source.read_text())
assert (data['planned'], data['terminal'], data['certified_lfd_at_least5'], data['other_terminal'], data['pending']) == (140, 136, 59, 77, 4)
assert data['pending_ids'] == [f'fresh-n45-rand-{i:02d}' for i in range(1, 5)]

table = ['| n | Planned | Terminal | Certified LFD ≥ 5 | Other terminal | Pending |',
         '|---:|---:|---:|---:|---:|---:|']
bars = []
for n in range(33, 46):
    row = data['counts_by_n'][str(n)]
    pending = row['planned'] - row['terminal']
    table.append(f"| {n} | {row['planned']} | {row['terminal']} | {row['certified_lfd_at_least5']} | {row['other_terminal']} | {pending} |")
    y = 48 + (n - 33) * 30
    scale = 28
    bound = row['certified_lfd_at_least5'] * scale
    other = row['other_terminal'] * scale
    missing = pending * scale
    bars.append(f'<text x="20" y="{y+17}" font-size="15" fill="#17222f">n={n}</text>'
                f'<rect x="105" y="{y}" width="{bound}" height="22" fill="#276b9a"/>'
                f'<rect x="{105+bound}" y="{y}" width="{other}" height="22" fill="#9aaab7"/>'
                f'<rect x="{105+bound+other}" y="{y}" width="{missing}" height="22" fill="#e2b34f"/>'
                f'<text x="{115+row["planned"]*scale}" y="{y+17}" font-size="14" fill="#17222f">{row["terminal"]}/{row["planned"]}</text>')
svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="495" viewBox="0 0 900 495" role="img" aria-label="Panel coverage by n: certified lower bounds, other terminal, and pending inputs">
<rect width="900" height="495" fill="white"/>
<g font-family="sans-serif">
<text x="20" y="28" font-size="20" fill="#17222f">Preregistered D4 panel coverage, n=33–45</text>
''' + '\n'.join(bars) + '''
<rect x="20" y="458" width="16" height="16" fill="#276b9a"/><text x="42" y="472" font-size="13">certified LFD ≥ 5</text>
<rect x="245" y="458" width="16" height="16" fill="#9aaab7"/><text x="267" y="472" font-size="13">other terminal</text>
<rect x="420" y="458" width="16" height="16" fill="#e2b34f"/><text x="442" y="472" font-size="13">pending</text>
<text x="650" y="472" font-size="13">units: inputs; n=33 includes 10 tr0</text>
</g></svg>'''
(report / 'coverage.svg').write_text(svg)
md = '''# D4 panel coverage through n=45

The preregistered plan has **140** named D4 inputs at n=33–45: ten per n, plus ten trace-zero inputs at n=33. The [coverage audit](../../validation/panel-coverage-20261031-001/coverage.json) matched **136 terminal records** to distinct planned IDs and checked their result and inference links. **59** records carry an LFD ≥ 5 lower bound; **77** other terminal records do not establish that lower bound. The four pending IDs are `fresh-n45-rand-01` through `fresh-n45-rand-04`. Random-01 is running, so it remains pending in this immutable snapshot.

''' + '\n'.join(table) + '''

![Panel coverage by n](coverage.svg)

The audit checks plan and inventory hashes, result identity, count and inference-chain arithmetic for the earlier expansion, and result hashes and strict count-versus-codimension inequalities for the later panel. It does **not** rehash or replay every large certificate. A terminal `producer_contains_one` or a checked codimension equal to the solution count stays in “other terminal”; neither yields an upper bound on LFD. This is a point-in-time coverage report, not a statistical estimate of the probability of a bound.
'''
(report / 'report.md').write_text(md)
rows = '\n'.join(f"n={n}: {data['counts_by_n'][str(n)]['terminal']}/{data['counts_by_n'][str(n)]['planned']} terminal, {data['counts_by_n'][str(n)]['certified_lfd_at_least5']} certified LFD≥5" for n in range(33, 46))
typ = '''#set page(paper: "a4", margin: 18mm)
#set text(size: 9.5pt)
= D4 panel coverage through n=45
The preregistered plan has 140 named D4 inputs at n=33–45: ten per n plus ten trace-zero inputs at n=33. The index audit matched 136 terminal records to distinct planned IDs. Fifty-nine carry an LFD-at-least-five lower bound. Seventy-seven other terminal records do not establish that lower bound. Four original n45 random inputs remain pending.

#image("coverage.svg", width: 100%)

''' + rows + '''

The audit verifies plan, inventory, result and inference links and strict count-versus-codimension arithmetic. It does not rehash or replay every large certificate. Other terminal outcomes are inconclusive for this lower bound, not upper bounds.
'''
(report / 'report.typ').write_text(typ)
typst.compile(str(report / 'report.typ'), output=str(report / 'report.pdf'))
manifest = {'schema': 'semaev.panel-coverage-report/v1', 'coverage_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
            'files': {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
                      for p in report.iterdir() if p.is_file() and p.name != 'manifest.json'}}
(report / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
