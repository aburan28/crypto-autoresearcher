"""Descriptive reports from existing immutable raw output; no scientific execution."""
from pathlib import Path
import argparse,json,shutil,datetime
import yaml
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst,pymupdf

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--experiment',required=True);ap.add_argument('--run',required=True);args=ap.parse_args()
 repo=args.repo.resolve();run=repo/'experiments'/args.experiment/'runs'/args.run
 receipt=json.loads((run/'execution-receipt.json').read_text());env=json.loads((run/'environment.json').read_text());raw=json.loads((run/'raw-result.json').read_text())
 stamp=datetime.datetime.fromisoformat(receipt['started_at']).strftime('%Y%m%dT%H%MZ');out=repo/'experiments'/args.experiment/'reports'/('run-'+stamp);out.mkdir(exist_ok=False,parents=True)
 cells=raw['cells'];n=len(cells);fig,ax=plt.subplots(figsize=(9,3.7))
 if args.experiment=='EXP-ECDLP-4c6a09':
  for kind in sorted({c['field']['kind'] for c in cells}):
   cc=[c for c in cells if c['field']['kind']==kind]
   ax.scatter([c['field']['d'] for c in cc],[c['rungs'][-1]['distinct_residues'] for c in cc],s=12,alpha=.45,label=f'{kind} (n={len(cc)})')
  ax.set(xlabel='Recorded field degree d',ylabel='Distinct fibre residues at final work rung',title=f'{n} recorded cells; all final-rung counts shown')
  limits='Rank descent was explicitly skipped by the producer; independent generator sets and rank gains are not certified. New non-torsion-point counts are not substituted for rank. The recorded gamma values are finite covering diagnostics, not an ECDLP complexity exponent.'
 else:
  for key,offset,label in [('rot',-.2,'rotation'),('hash',0,'keyed hash'),('size_random_prime',.2,'size / random prime')]:
   ax.errorbar([c['c']+offset for c in cells],[c[key]['closure_ratio'] for c in cells],yerr=[c[key]['closure_ratio_se'] for c in cells],fmt='.',ms=4,alpha=.45,label=label)
  ax.set(xlabel='Exponent c / matched random-prime bit length',ylabel='Recorded closure ratio (bars: recorded 1 SE)',title=f'{n} cells; all fixed seeds, curves and m values')
  limits='Closure statistics are bounded finite measurements. Recorded one-standard-error bars are displayed literally; no new significance test, confidence interval or asymptotic inference is made. Negation symmetry and equal-density controls remain as specified by the producer.'
 ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'observations.svg');plt.close(fig)
 checker=(run/'check.stdout.log').read_text().strip()
 try:checkdesc=json.dumps(json.loads(checker),sort_keys=True)
 except ValueError:checkdesc=checker[:1400]
 text=[
  'Observations only. This is a descriptive run report, not hypothesis review, scientific promotion, or an execution-proof claim.',
  f'Experiment {args.experiment}; goal GOAL-ECDLP-001; run {args.run}. Source-at-launch commit {env["commit"]}. All source bindings and literal argv are in environment.json and command.txt.',
  f'One frozen full-grid trial produced {n} saved cells. Producer return code {receipt.get("returncode")}; checker return code {receipt.get("check_returncode")}; supervisor outcome {receipt["status"]}. Detail: {receipt.get("detail")}.',
  f'Start {receipt["started_at"]}; finish {receipt["finished_at"]}. The producer manifest records available wall timing. CPU usage, detailed hardware, and dirty-tree state are not recorded by this legacy supervisor. The exact memory/watchdog envelope and seeds are in the frozen trial plan and command.txt.',
  f'Execution-time checker output (observed): {checkdesc}',
  limits,
  'All cells, controls, failed/censored outcomes and null values remain in raw-result.json. A checker pass does not independently review every mathematical claim. Schema/accounting corrections preserve the original supervisor receipt and cannot retroactively change invalid_output into output_validated.',
  'Graph plots recorded observations only. No performance or attack-cost claim is made. Scientific source digests are frozen at launch; unrelated control-plane commits while the process runs do not change those source bytes. Producer end-of-run git HEAD, if different, is separate from execution source identity.',
  f'Artifacts: ../../runs/{args.run}/ (launch.json, environment.json, command.txt, raw-result.json, manifest.yaml, execution-receipt.json, stdout/stderr and checker logs). No deployed-key recovery or NFS sieving occurred.'
 ]
 (out/'report.md').write_text('# Frozen-grid run observations\n\n'+'\n\n'.join(text)+'\n')
 source='#set page(paper:"a4", margin:16mm)\n#set text(size:9pt)\n= Frozen-grid run observations\n'+'\n\n'.join('#text('+json.dumps(p)+')' for p in text[:4])+'\n\n#image("observations.svg",width:100%)\n\n'+'\n\n'.join('#text('+json.dumps(p)+')' for p in text[4:])
 (out/'report.typ').write_text(source);typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'),root=str(repo))
 shutil.copyfile(__file__,out/'render_existing_run.py')
 pdf=pymupdf.open(out/'report.pdf')
 for i,page in enumerate(pdf):
  print('PAGE',i+1,page.get_text());page.get_pixmap(matrix=pymupdf.Matrix(1,1)).save(f'/tmp/{args.run}-report-page-{i+1}.png')
 print(json.dumps({'report':str(out),'pages':len(pdf),'cells':n}))

if __name__=='__main__':main()
