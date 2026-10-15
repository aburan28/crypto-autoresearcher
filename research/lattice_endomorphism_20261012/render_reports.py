#!/usr/bin/env python3
"""Render scoped research and observation reports from recorded artifacts.

Rendering dependencies: Graphviz dot, matplotlib and the typst Python wheel.
The drivers/supervisor do not depend on these presentation tools.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import textwrap


def literal(text):
    return json.dumps(text, ensure_ascii=False)


def pdf(directory, title, paragraphs, visuals):
    import typst
    lines = ['#set page(paper: "a4", margin: 18mm)', '#set text(size: 10pt)',
             '#set par(justify: false)', '= ' + title]
    for heading, text in paragraphs:
        lines += ['== ' + heading, '#text(' + literal(text) + ')', '']
    for caption, filename in visuals:
        width = '55%' if filename == 'flow.svg' else '100%'
        lines += ['#figure(image(' + literal(filename) + ', width: ' + width + '), caption: ' + literal(caption) + ')']
    source = directory / 'report.typ'
    source.write_text('\n'.join(lines) + '\n')
    typst.compile(str(source), output=str(directory / 'report.pdf'))


def diagram(directory, record):
    labels = {
        'hom-degree-forms': ['Supplied CM Hom basis', 'Degree form: Delta and content',
                             'Product graph plus full-form constraints', 'Unknown full Hom / actual curve lift'],
        'transport-denominators': ['Supplied primitive CM generator', 'Rational matrix transport',
                                   'Full kernel/module action plus conductor anchor', 'Actual maps and geometric torsion'],
        'order-saturation': ['Supplied CM order and candidate generators', 'Norm/index selection diagnostics',
                             'Faithful full-module division check', 'Map discovery and complete cost accounting'],
        'quaternion-volume': ['Supplied Hurwitz quaternion order, p=2', 'Rank and trace Gram determinant',
                              'Unit, closure and maximality checks', 'Odd-p curves / characteristic-prime lift'],
    }[record['slug']]
    dot = 'digraph research { rankdir=TB; graph [bgcolor="white",ranksep=0.35]; node [shape=box,style="rounded,filled",fillcolor="#eff6ff",fontname="Helvetica",fontsize=14]; edge [fontsize=12];\n'
    for i, label in enumerate(labels):
        dot += f'n{i} [label={literal(textwrap.fill(label, width=24))}];\n'
    dot += 'n0 -> n1 [label="exact supplied fixtures"]; n1 -> n2 [label="necessary checks"]; n2 -> n3 [style=dashed,label="open research obligation"];\n}\n'
    (directory / 'flow.dot').write_text(dot)
    subprocess.run(['dot', '-Tsvg', str(directory / 'flow.dot'), '-o', str(directory / 'flow.svg')], check=True)


def search_report(root, record):
    study = root / 'research/lattice_endomorphism_20261012' / record['slug']
    diagram(study, record)
    title = record['slug'].replace('-', ' ').title() + ': exploration and experiment design'
    description = (study / 'exploration.md').read_text()
    paragraphs = [
        ('Status and scope', 'This is a research-design report, not an evidence-review verdict. Novelty is unverified. '
         'All initial instances are supplied exact synthetic lattices with planted ambient orders. '
         'No finite-field map discovery, performance advantage or ECDLP consequence is established.'),
        ('Records and implementation', f"Question {record['question_id']}; hypothesis {record['hypothesis_id']}; "
         f"experiment {record['experiment_id']}. Driver {record['tool']}. Tracking issue {record['tracking_issue_url']}. "
         'The companion exploration.md contains the derivations, primary-source read receipts, controls and next experiments.'),
        ('Method and controls', 'The frozen protocol retains complete-assumption fixtures alongside incomplete bases, '
         'nonprimitive generators, misleading partial modules, scalar/collinear maps, and rank/index/closure collisions as applicable. '
         'Run integrity replay and software regression checks are distinct from independent mathematical review.'),
        ('Source and canonical graph policy', 'Sources and their actual read scopes are recorded in exploration.md and the proposal. '
         'Primary pointers: Kani, https://doi.org/10.1007/s13348-010-0029-1; Bisson/Sutherland, https://arxiv.org/abs/0902.4670; '
         'Fuselier et al., https://aiezzi.it/documents/art7.pdf; Voight, https://math.dartmouth.edu/~jvoight/quat-book.pdf. '
         'The ECDLP frontier map was checked for positioning and left unchanged: this work asserts no ECDLP frontier or scientific-status change. '
         'This diagram presents a supplied-object workflow; its dashed edge is an unimplemented research obligation.'),
        ('Next action', record.get('next_action', 'Execute the frozen admitted pilot, retain its observations, and obtain independent review before any conclusion.')),
    ]
    report = '# ' + title + '\n\n' + '\n\n'.join('## ' + h + '\n\n' + t for h, t in paragraphs)
    report += '\n\nSee [exploration.md](exploration.md), [flow.svg](flow.svg), and [report.pdf](report.pdf).\n'
    (study / 'report.md').write_text(report)
    (study / 'source-note.json').write_text(json.dumps({'exploration_sha256': hashlib.sha256(description.encode()).hexdigest(),
                                                       'interpretation': 'design only; no scientific promotion'}, indent=2) + '\n')
    pdf(study, title, paragraphs, [('Proposed workflow and explicit unresolved interface.', 'flow.svg')])


def observation_report(root, record):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    exp = root / 'experiments' / record['experiment_id']
    run_dir = exp / 'runs' / record['run_id']
    raw = json.loads((run_dir / 'raw-result.json').read_text())
    receipt = json.loads((run_dir / 'execution-receipt.json').read_text())
    launch = json.loads((run_dir / 'launch.json').read_text())
    env = json.loads((run_dir / 'environment.json').read_text())
    started = launch['started_at']
    stamp = started[:16].replace('-', '').replace(':', '') + 'Z'
    out = exp / 'reports' / ('run-' + stamp)
    out.mkdir(parents=True, exist_ok=False)
    slug = record['slug']
    if slug == 'hom-degree-forms':
        item = next(t for t in raw['triangles'] if t['planted'] == [6, 10, 12])
        labels = ['vertex 0', 'vertex 1', 'vertex 2']
        series = {'planted': item['planted'], 'complete basis': item['recovered'],
                  'uniform-two product-only': item['uniform_two_naive_recovered']}
        y_label = 'conductor (integer)'
        sample = 'One retained triangle (6,10,12); scaled product-only answer is rejected by the full-form gate.'
    elif slug == 'transport-denominators':
        item = next(c for c in raw['cases'] if c['D_K'] == -4 and c['planted_conductors'] == [1, 6])
        labels = ['k=1', 'k=2', 'k=3']
        series = {'standard target denominator': [a['standard_target_denominator'] for a in item['arms']]}
        y_label = 'least denominator (integer)'
        sample = 'One retained ordered pair D_K=-4, f_i=1, f_j=6; three generator scales.'
    elif slug == 'order-saturation':
        item = next(c for c in raw['cases'] if c['D_K'] == -4 and c['planted_order_conductor'] == 1)
        labels = [p['policy'].replace('_', ' ') for p in item['policies']]
        series = {'selected supplied generators': [p['selected_generators'] for p in item['policies']]}
        y_label = 'selected generators (count)'
        sample = 'One retained supplied pool. Scoring and map-acquisition costs are incomplete; this is not a speedup comparison.'
    else:
        labels = ['Hurwitz', 'Lipschitz', 'nonclosed index 4', 'closed index 4']
        names = ['hurwitz', 'lipschitz', 'nonclosed_index_four', 'closed_index_four']
        series = {'additive index in Hurwitz': [next(c for c in raw['lattice_controls'] if c['label'] == name)['index_in_hurwitz']
                                                for name in names]}
        y_label = 'additive lattice index (integer)'
        sample = 'Four retained lattice controls. Equal additive index does not certify multiplicative closure.'
    plot_data = {'labels': labels, 'series': series, 'y_label': y_label, 'sample': sample,
                 'run_id': record['run_id'], 'source': str(run_dir.relative_to(root) / 'raw-result.json'),
                 'uncertainty': 'not applicable: deterministic exact fixtures; no stochastic population claim'}
    (out / 'plot-data.json').write_text(json.dumps(plot_data, indent=2) + '\n')
    # Editable rendering source reproduces only recorded values, no new experiments.
    (out / 'plot.py').write_text('import json\nfrom pathlib import Path\nimport matplotlib\nmatplotlib.use("Agg")\nimport matplotlib.pyplot as plt\n'
        'd=json.loads(Path(__file__).with_name("plot-data.json").read_text())\nfig,ax=plt.subplots(figsize=(8,3.5))\n'
        'width=0.75/len(d["series"])\nfor k,(name,values) in enumerate(d["series"].items()):\n'
        ' ax.bar([i+k*width for i in range(len(values))],values,width=width,label=name)\n'
        'ax.set_xticks([i+width*(len(d["series"])-1)/2 for i in range(len(d["labels"]))],d["labels"])\n'
        'ax.set_ylabel(d["y_label"])\nax.legend(fontsize=8)\nfig.tight_layout()\n'
        'fig.savefig(Path(__file__).with_name("observations.svg"))\n')
    subprocess.run(['python3', str(out / 'plot.py')], check=True)
    title = slug.replace('-', ' ').title() + ': deterministic pilot observations'
    paragraphs = [
        ('Observation-only status', 'This report records execution outputs; it makes no support, weakening, priority or scientific-status decision. '
         'Independent mathematical review remains separate. All instances are supplied synthetic lattices.'),
        ('Trial and provenance', f"Experiment {record['experiment_id']}; hypothesis {record['hypothesis_id']}; run {record['run_id']}. "
         f"Code commit {env['commit']}. Seed {raw['seed']}. Exact command: " + json.dumps(launch['argv']) + '. '
         'One trial requested; completion/failure and resource observations are preserved in execution-receipt.json. '
         'The driver records full-tree dirtiness as unknown when not supplied; every source byte is admitted against its committed hash.'),
        ('Recorded outputs', 'Exact fixture counters (integer counts, not independent statistical samples): ' + json.dumps(raw['checks'], sort_keys=True)
         + '. Supervisor receipt: ' + json.dumps(receipt, sort_keys=True)[:2200]),
        ('Control scope and graph', sample + ' All plotted values come directly from raw-result.json; no new sampling is performed. '
         'Uncertainty bars are inapplicable to these deterministic exact values. Plot source and extracted data are retained.'),
        ('Limitations and missing data', ' '.join(raw['limitations']) + ' The integrity checker replays the implementation; '
         'it is not independent research review. No ECDLP canonical graph or frontier was changed.'),
    ]
    md = '# ' + title + '\n\n' + '\n\n'.join('## ' + h + '\n\n' + t for h, t in paragraphs)
    md += '\n\n[Recorded-value plot](observations.svg) · [PDF](report.pdf)\n'
    (out / 'report.md').write_text(md)
    pdf(out, title, paragraphs, [(sample + ' Run ' + record['run_id'] + '.', 'observations.svg')])
    plt.close('all')
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('.'))
    p.add_argument('--slug', required=True)
    p.add_argument('--kind', choices=('search', 'run'), required=True)
    args = p.parse_args()
    root = args.root.resolve()
    record = json.loads((root / 'research/lattice_endomorphism_20261012' / args.slug / 'tracking.json').read_text())['record']
    if args.kind == 'search':
        search_report(root, record)
    else:
        print(observation_report(root, record))


if __name__ == '__main__':
    main()
