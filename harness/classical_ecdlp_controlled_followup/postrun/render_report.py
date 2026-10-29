"""Two-panel descriptive report, SVG source and standalone PDF; failures retained."""
from pathlib import Path
import json
import html


def render(root):
    root=Path(root); export=json.loads((root/'postrun-result.json').read_bytes())
    path=root/'analysis.json'
    if not path.exists():path=root/'partial-analysis.json'
    data=json.loads(path.read_bytes()) if path.exists() else {'per_curve_six_cell':[]}
    rows=data['per_curve_six_cell']
    report=['# Controlled follow-up retained observations','','Operational export: '+export['status']+'. Scientific validity: not assessed.','',
            'No qualified clocks or independent counter replay. Native RSS, interpreter allocation, I/O and integer internals are unmetered.','',
            'Curve is the population unit; six cells share a trace. No significance or scalar-ordering conclusion.','',
            '| Curve | Cell | Successes / attempts | Outcomes |','|---|---|---|---|']
    for r in rows:report.append('| '+r['curve_id']+' | '+r['cell']+' | '+str(r['successes'])+' / '+str(r['attempts'])+' | '+json.dumps(r['outcomes'],sort_keys=True)+' |')
    report+=['','Failures: '+json.dumps(export['errors'],sort_keys=True),'','All raw records and cost vectors are linked in export.json; undefined ratios stay null.']
    (root/'report.md').write_text('\n'.join(report)+'\n')
    # A two-panel plot: exact recovery fractions; retained operational outcome counts.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for i,r in enumerate(rows):
        axes[0].scatter(i,r['successes']/r['attempts'] if r['attempts'] else 0,s=12)
    axes[0].set(title='Per-curve, per-cell retained fractions',xlabel='Retained curve/cell index',ylabel='Success events / attempts',ylim=(-.02,1.02))
    counts={}
    for r in rows:
        for k,v in r['outcomes'].items():counts[k]=counts.get(k,0)+v
    if counts:
        axes[1].bar(range(len(counts)),list(counts.values()));axes[1].set_xticks(range(len(counts)),list(counts),rotation=30,ha='right')
    else:axes[1].text(.5,.5,'No complete cells retained',ha='center',va='center')
    axes[1].set(title='All retained outcome states',ylabel='Cells')
    fig.suptitle('Operational export: '+export['status']+'; descriptive only; wall_valid=false')
    fig.tight_layout();fig.savefig(root/'report.svg')
    from matplotlib.backends.backend_pdf import PdfPages
    import textwrap
    with PdfPages(root/'report.pdf') as pdf:
        text=plt.figure(figsize=(8.3,11.7));text.text(.06,.95,'\n'.join(textwrap.fill(line,100) for line in report[:24]),va='top',fontsize=8)
        pdf.savefig(text);plt.close(text);pdf.savefig(fig)
    plt.close(fig)
