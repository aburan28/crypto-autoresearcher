from pathlib import Path
import json,sys,platform
repo=Path('/workspace/snfs-research-pr');report=repo/'experiments/EXP-ECDLP-8cc60d/reports/run-20261017T1824Z';run=report.parents[1]/'runs/RUN-ECDLP-2ac930'
sys.path[:0]=['/workspace/snfs-toolchains/report','/workspace/snfs-ecdlp-experiments/vendor']
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst,pymupdf
raw=json.loads((run/'raw-result.json').read_text());receipt=json.loads((run/'execution-receipt.json').read_text());env=json.loads((run/'environment.json').read_text());checked=json.loads((run/'check.stdout.log').read_text())
n=sum(len(c['census']['rows']) for c in raw['part_a']['cells'])
fig,ax=plt.subplots(figsize=(9,3.5))
for arm,color,off in [('mersenne','#176b92',-.15),('random','#ca7627',.15)]:
 xs=[];ys=[]
 for c in raw['part_a']['cells']:
  if c['census']['arm']!=arm:continue
  for r in c['census']['rows']:xs.append(c['c']+off);ys.append(r['k']/r['l'])
 ax.scatter(xs,ys,s=7,alpha=.3,label=arm,color=color)
ax.set(xlabel='Mersenne exponent c / matched random prime bit length',ylabel='Recorded k divided by subgroup prime l',xticks=[13,17,19,31],ylim=(-.03,1.03),title=f'Raw embedding-degree ratios, {n} rows across 24 cells')
ax.legend();fig.tight_layout();fig.savefig(report/'embedding-ratios.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(9,2.8))
cells=raw['part_b']['cells'];x=list(range(len(cells)))
ax.plot(x,[c['observed'] for c in cells],'o-',label='Recorded count')
ax.plot(x,[c['predicted_mean_upper'] for c in cells],'s--',label='Recorded model mean upper')
ax.set(yscale='log',xlabel='Cell index (3 seeds × 4 exponents)',ylabel='Count / modeled count (log scale)',title='Small-order census: recorded observations and model values')
ax.legend();fig.tight_layout();fig.savefig(report/'small-order-counts.svg');plt.close(fig)
text=f'''Observations only. This report does not review or promote any hypothesis. The supervisor recorded invalid_output; corrected metadata must not be described as retroactive output validation.
Experiment EXP-ECDLP-8cc60d; hypothesis H-ECDLP-281dd6; goal GOAL-ECDLP-001. Run RUN-ECDLP-2ac930. Launch commit {env['commit']}.
One full-grid trial ran. The scientific process exited {receipt['returncode']} and the checker exited {receipt['check_returncode']}. Its check log reports {json.dumps(checked['checked'],sort_keys=True)} with no reported problems. The checker checks retained samples; that is not independent review of every row.
The saved output contains {n} part-A rows in 24 cells, 12 part-B cells, 4 public-parameter part-C rows and 3 part-D boxes. Raw data, controls, seeds 1,2,3, exact argv, source digests and environment are retained under ../../runs/RUN-ECDLP-2ac930/. No sieving or key recovery was performed.
The required manifest schema failed: {receipt['detail']}. Scientific raw output and checker success remain observations, with output_validated coverage zero and scientific review absent.
Start {receipt['started_at']}; finish {receipt['finished_at']}. CPU usage is not recorded by this supervisor. The legacy producer manifest records its elapsed wall time. Dirty-tree state and detailed hardware are unavailable in this receipt. The process ran within the frozen 7,200-second / 1,024-MiB envelope.
Graph 1 plots the arithmetic ratio k/l from recorded rows; graph 2 plots already recorded counts and model means without new estimation. No confidence interval is inferred. Model mismatches stay visible and are not a scientific rejection. Part-D values are polynomial norm diagnostics, not completed DLP or sieve performance.
Artifacts: execution-receipt.json, launch.json, command.txt, environment.json, manifest.yaml, raw-result.json and all stdout/stderr and checker logs in the run directory. Missing structured run-manifest provenance is tracked by problems/ready-plans-lack-supervisor-archive-coverage.md. Original bytes remain immutable.
'''
(report/'report.md').write_text('# G2 full-grid observations\n\n'+text)
parts=text.split('\n');source='#set page(paper: "a4", margin: 16mm)\n#set text(size: 9pt)\n= G2 full-grid observations\n'
source+='\n\n'.join('#text('+json.dumps(p)+')' for p in parts[:5])
source+='\n\n#image("embedding-ratios.svg", width:100%)\n\n#image("small-order-counts.svg", width:100%)\n\n'
source+='\n\n'.join('#text('+json.dumps(p)+')' for p in parts[5:] if p)
(report/'report.typ').write_text(source);typst.compile(str(report/'report.typ'),output=str(report/'report.pdf'),root=str(repo))
pdf=pymupdf.open(report/'report.pdf')
for i,p in enumerate(pdf):
 print('PAGE',i+1,p.get_text());p.get_pixmap(matrix=pymupdf.Matrix(1,1)).save('/tmp/snfs-g2-report-page-'+str(i+1)+'.png')
print('pages',len(pdf),'rows',n)
