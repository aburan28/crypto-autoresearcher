#!/usr/bin/env python3
"""Derived communication only: read sealed records; never import/run the producer."""
import argparse,copy,gzip,hashlib,json,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()) if p.name.endswith('.gz') else p.read_bytes())
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def num(v):return f'{v:,}'
def main():
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['prepare','render']);a.add_argument('--repo',required=True);a.add_argument('--out',required=True);a.add_argument('--outer',required=True);z=a.parse_args()
 repo=Path(z.repo);out=Path(z.out);outer=Path(z.outer);run=repo/'experiments/EXP-ECDLP-787704/runs/RUN-ECDLP-53b08d';receipt=load(run/'execution-receipt.json');summary=load(run/'summary.json.gz');raw=load(run/'export.json');process=load(run/'process.json.gz');launch=load(run/'launch.json')
 bindings={}
 for n,h in receipt['artifact_sha256'].items():
  p=run/n
  if digest(p)!=h:raise ValueError('native member changed: '+n)
  bindings[n]=dict(sha256=h,bytes=p.stat().st_size)
 aggregates=[]
 for t in range(3):
  for e in (0,2):
   rows=[q for q in summary['rows'] if(q['radius'],q['erasure_cap'])==(t,e)];totals=Counter();hist={k:Counter() for k in rows[0]['histograms']}
   for q in rows:
    totals.update(q['totals'])
    for k,v in q['histograms'].items():hist[k].update(v)
   aggregates.append(dict(radius=t,erasure_cap=e,curves=len(rows),states=sum(q['states'] for q in rows),totals=dict(totals),histograms={k:dict(v) for k,v in hist.items()},zero_q_curves=sum(q['q'][0]==0 for q in rows),q_min=min(q['q'][0]/q['q'][1] for q in rows),q_max=max(q['q'][0]/q['q'][1] for q in rows)))
 if z.mode=='prepare':
  observations=dict(schema='exact-density.descriptive-observations/v1',run_id=receipt['run_id'],raw_commit='2b3c2f791aa964db6bdf2eefd62a6a8ed72b1130',scientific_validity='not_assessed',kind='Arithmetic and transcription from immutable recorded complete census; no new enumeration.',source_bindings=bindings,native_receipt=receipt,all_288_curve_cell_rows=summary['rows'],all_48_curve_bindings=summary['curves'],cell_aggregate_counts=aggregates,diagnostic_work=summary['diagnostic_work'],controls=load(run/'controls.json'),regression=load(run/'regression.json.gz'),inner_process_metadata={k:v for k,v in process.items() if k!='children'},actual_native_argv=launch['argv'],limits=['Exact fractions describe these recorded finite fixed functions only; independent mathematical validation remains separate.','No iid population inference, attack-cost, speedup, exponent, novelty or expected-retry claim.','Native structural output validation does not imply frozen-protocol export conformance.'])
  write(out/'observations.json',observations)
  data=dict(run_id=receipt['run_id'],source_summary_sha256=digest(run/'summary.json.gz'),curve_order=[x['curve_id'] for x in summary['curves']],rows=[{k:q[k] for k in ('curve_id','radius','erasure_cap','q','uniform_reference')} for q in summary['rows']],display='All48 curves in original order; all6 cells, including all exact zeros. Percent scale; no sampling uncertainty on finite complete-domain arithmetic.')
  write(out/'plot-data.json',data)
  derived=copy.deepcopy(raw);prefix='runs/RUN-ECDLP-53b08d/'
  for f in derived['files']:f['path']=prefix+f['path']
  for r in derived['runs']:
   for f in r['artifacts']:f['path']=prefix+f['path']
  derived['host']['path']=prefix+derived['host']['path']
  derived['export_id']=raw['export_id']+'.path-rebased';derived['created']=datetime.now(timezone.utc).isoformat()
  derived['notes'].append(dict(kind='observation',by='TASK-20261030-fafaa1',text='Explicitly derived one-bundle view: only file/host/artifact paths rebased relative to outer export. Raw export SHA256 '+digest(run/'export.json')+'; raw source commit cb9953014fe0d93f193c3892d73bd284348532ae and backend_record/seals unchanged. Original analysis.script remains null; no cloned rows or analytical-arm executions. Derivation script reports/run-20261030T1722Z/render_report.py SHA256 '+digest(Path(__file__))+'. Frozen-protocol conformance remains qualified; actual checker outcome retained beside report.'))
  if derived['backend_record']!=raw['backend_record'] or derived['runs'][0]['measurements']!=raw['runs'][0]['measurements']:raise ValueError('raw semantics changed')
  write(outer,derived);return
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 import matplotlib.ticker as mt
 plt.rcParams.update({'font.size':9,'svg.fonttype':'none','font.family':'DejaVu Sans'})
 fig,axes=plt.subplots(3,2,figsize=(10.4,8.3),sharex=True,sharey=True,layout='constrained')
 ymax=max(max(q['q'][0]/q['q'][1],q['uniform_reference'][0]/q['uniform_reference'][1]) for q in summary['rows'])*1.08
 for ax,ag in zip(axes.flat,aggregates):
  rows=[q for q in summary['rows'] if(q['radius'],q['erasure_cap'])==(ag['radius'],ag['erasure_cap'])];x=list(range(1,49))
  ax.plot(x,[q['q'][0]/q['q'][1] for q in rows],color='#1552a0',marker='o',markersize=3,lw=0.8,label='Recorded q')
  ax.plot(x,[q['uniform_reference'][0]/q['uniform_reference'][1] for q in rows],color='#bd6200',marker='x',markersize=3,lw=.8,linestyle='--',label='Matched uniform reference')
  ax.set_title(f"t={ag['radius']}, erasure cap={ag['erasure_cap']} | zero-q curves {ag['zero_q_curves']}/48",fontsize=9)
  ax.set_ylim(-ymax*.025,ymax);ax.set_xlim(.3,48.7);ax.grid(alpha=.2);ax.yaxis.set_major_formatter(mt.PercentFormatter(1));ax.set_xticks([1,12,24,36,48]);ax.axhline(0,color='#666',lw=.5)
  for cut in (12.5,24.5,36.5):ax.axvline(cut,color='#bbb',ls=':',lw=.6)
 axes[0,0].legend(loc='upper right',fontsize=7);fig.suptitle('RUN-ECDLP-53b08d | all48 retained primary fixed functions',fontsize=12)
 fig.supxlabel('Curve index in original cohort order (1–12 discovery;13–24 validation;25–48 confirmation A/B)');fig.supylabel('Recorded finite-domain fraction (dimensionless, displayed as %)')
 fig.savefig(out/'study-map.svg');plt.close(fig)
 validation=load(out/'export-validation.json');gap=validation['returncode'];findings=validation['stdout']
 table=[];wordtable=[]
 for ag in aggregates:
  c=ag['totals'];st=ag['histograms']['status'];cap=ag['histograms']['capped'].get('True',0)
  table.append([f"{ag['radius']}/{ag['erasure_cap']}",num(c['successes']),num(st.get('EMPTY_INTERVAL',0)),num(st.get('REJECTED_FINAL_VERIFICATION',0)),num(st.get('UNDEFINED',0)),num(cap),num(c['zero_checks']),str(ag['zero_q_curves'])])
  wordtable.append([f"{ag['radius']}/{ag['erasure_cap']}",num(c['words']),num(c['legal']),num(c['empty']),num(c['sumM']),num(c['transformed_false'])])
 command=' '.join(launch['argv']);start=receipt['started_at'];finish=receipt['finished_at']
 from datetime import datetime as dt
 elapsed=(dt.fromisoformat(finish)-dt.fromisoformat(start)).total_seconds()
 base='''This report describes recorded outputs and derived arithmetic, not an evidence review or scientific verdict. The native complete census reports 48 fixed primary functions,821638 nonzero scalar states and288 curve-cell summaries. Scientific validity remains not_assessed; independent mathematical validation and frozen-protocol export conformance remain outstanding.'''
 scope='''EXP-ECDLP-787704 · H-ECDLP-6674c9 · GOAL-ECDLP-e70832. One physical census invocation, RUN-ECDLP-53b08d, used circuit2.a1 (alpha=-2,beta=-1,a=b=1) on each retained public-cohort base. Each s=1,…,r−1 was recorded once per curve and evaluated in all six (t,e_cap) cells. No new curves, targets, reference bank or entropy were introduced. Denominators and exact fractions are retained for every curve/cell in observations.json and plot-data.json.'''
 method='''Recorded q=Nsuccess/(r−1). The matched conditional-uniform reference is sum_s M(s)/(r−1)^2, where M counts distinct legal nonzero candidates; zero candidates remain paid checks. These fractions describe complete finite fixed-function domains, so no binomial interval or iid curve-family claim is supplied. The comparison is descriptive and is not an attack-cost comparison.'''
 status='''Native execution-receipt: output_validated, actual driver0/checker0, published=false, scientific_conclusion=null. The published=false field is the immutable native framework capture and is not overwritten by later Git publication. Inner process.returncode=null and termination=pending_outer_supervisor_exit are captured before its eventual exit; actual termination comes from the outer receipt. No native failed or timed-out trial is recorded in this one-trial session.'''
 limit='''All918 erasure-bearing states have exactly one erased bit. They are capped in every e_cap=0 cell; t0/e0 retains original UNDEFINED status, while t1/e0 and t2/e0 use CAPPED_ERASURES. No state has two or more erasures in this recorded panel. All-zero density curves, rejected states, empty intervals and zero candidate checks remain included. Controls and retained regression explicitly say not_run in this census; fixed controls were separate pre-admission work, and full independent new/retained validation remains separate.'''
 costs=f'''Recorded diagnostic work: {num(summary['diagnostic_work']['word_visits'])} word visits; {num(summary['diagnostic_work']['public_equation_certifications'])} public-equation certifications; {num(summary['diagnostic_work']['distinct_nonzero_reference_additions'])} distinct-nonzero reference additions. All49 child processes (one compiler,48 curve enumerations) recorded RC0 and unchanged source snapshots. Full public-orbit/predicate/label preparation and table certificates are separately paid diagnostic computation, not attack execution or old primitive counters. The supervisor start/finish timestamps span {elapsed:.6f}s (derived elapsed, unqualified); wall_valid=false. CPU totals, per-child RSS, native primitive weights and end-to-end attack cost are unknown. process.ru_maxrss records142392KiB for driver and child lifetime maxima (neither a summed nor per-invocation RSS bound).'''
 prov='''Actual execution source commit cb9953014fe0d93f193c3892d73bd284348532ae; dirty state null. Raw archive commit2b3c2f791aa964db6bdf2eefd62a6a8ed72b1130. Python3.12.14; Linux6.18.55 x86_64,5 logical CPUs recorded; CPU model/memory/isolation unknown. g++14.2.0 with -std=c++17 -O3 -DNDEBUG -Wall -Wextra -Werror. Compiled binary SHA256 de5afb21cf32a7c1a64c7feea5efb6247539926972ffda96977fa17e6557fbdf (22192 bytes). Runtime lock null; seed null because enumeration is deterministic. Full executed argv and source/member bindings are in observations.json and immutable launch/environment/process/source records.'''
 gaptext='''The original native export passed native structural checks but the unchanged frozen-protocol export checker returned RC1 with seven findings. The explicitly derived outer export rebases file/host/artifact paths, preserves the actual one bundle and cb995 source commit, keeps raw backend_record/seals unchanged, and leaves the absent frozen analysis.script explicit. Its actual check again returns RC'''+str(gap)+'''. No03be source substitution,96 cloned rows, protocol edit or forced green result is used. The original check lacked timestamps/full-source capture; those historical fields remain null. This report's check has actual times and source captures. The linked export-conformance problem remains open; none of these administrative mismatches is a mathematical refutation.'''
 md='# Exact finite-density census: recorded observations\n\n'+base+'\n\n'+scope+'\n\n'+method+'\n\n| t/cap | Recovered | Empty status | Rejected status | Undefined | Capped flag | Zero checks | q=0 curves |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'+'\n'.join('| '+' | '.join(row)+' |' for row in table)+'\n\nCounts aggregate all48 curves; each cell has821638 states. Aggregated counts are not one fixed-function q.\n\n'+limit+'\n\n![All48 curves and six cells](study-map.svg)\n\n'+status+'\n\n'+costs+'\n\n'+prov+'\n\nActual start: '+start+'; outer finish: '+finish+'.\n\n```text\n'+command+'\n```\n\n'+gaptext+'\n\n```text\n'+findings+'\n```\n\nSources: runs/RUN-ECDLP-53b08d/{execution-receipt.json,summary.json.gz,inputs.json,process.json.gz,export.json}; protocol.json; report export-validation.json; problems/classical-ecdlp-exact-density-export-conformance.md. All288 full rows/histograms are retained in observations.json. No canonical knowledge/claim graph was promoted; study-map.svg is this descriptive report’s new derived view.\n'
 (out/'report.md').write_text(md)
 def text(x):return '#text('+json.dumps(x,ensure_ascii=False)+')'
 def para(x):return text(x)+'\n\n'
 def tab(headers,rows,widths):return '#table(columns: ('+','.join(str(w)+'fr' for w in widths)+'), inset:4pt, stroke:0.3pt, table.header('+','.join('['+x+']' for x in headers)+'),'+','.join('['+v+']' for row in rows for v in row)+')\n'
 typ='''#set page(paper:"a4",margin:(x:15mm,y:14mm),numbering:"1")
#set text(font:"DejaVu Sans",size:9pt)
#set par(justify:false,leading:0.5em)
#set heading(numbering:none)
= Exact finite-density census: recorded observations
'''+para(base)+para(scope)+para(method)+'== Complete panel counts\n'+tab(['t/cap','Recovered','Empty','Rejected','Undef.','Cap flag','Zero checks','q=0 curves'],table,[.7,1,1,1.3,.8,.8,1,1])+para('Counts aggregate all48 curves; each cell has821638 states. Aggregate success counts are not one fixed-function q. Empty/rejected/undefined are state statuses; cap flags are separate and overlap t0/e0 UNDEFINED.')+para(limit)+'== Status and scope\n'+para(status)+'#pagebreak()\n= All recorded curve-cell fractions\n#image("study-map.svg",width:100%)\n'+para('All288 curve-cell pairs are plotted in original cohort order, including exact zeros; blue circles show recorded q, orange crosses show the matched conditional-uniform reference. RUN-ECDLP-53b08d; data and exact rational numerators/denominators: plot-data.json. Full finite enumeration has no sampling error bar. No family transfer or attack-cost inference.')+'#pagebreak()\n= Execution, costs and export qualification\n'+para(costs)+tab(['t/cap','Words','Legal','Empty words','sum M','False per check'],wordtable,[.7,1.3,1.2,1.2,1.3,1.3])+para('Both public equations were certified for every legal word, including zero and rejected candidates. False per check is the recorded transformed-false count and separately equals original-false; no short-circuit charge is inferred.')+para(prov)+para('Actual UTC interval: '+start+' to '+finish+'. Native exact command (line-wrapped only):')+'#text(size:6.6pt)[\n'+text(command)+'\n]\n'+para(gaptext)+'#text(size:7pt)[\n'+text(findings)+'\n]\n'+para('Evidence paths: experiments/EXP-ECDLP-787704/runs/RUN-ECDLP-53b08d/ and reports/run-20261030T1722Z/. Full288 rows/histograms: observations.json. Original/current export captures: admin-raw-report-actual/ and export-validation.json. Problem: problems/classical-ecdlp-exact-density-export-conformance.md. This new quantitative view changes no canonical knowledge/claim graph; independent validation remains separate.')
 (out/'report.typ').write_text(typ)
 import typst
 typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
 # Recheck immutable native input bindings after deriving every report artifact.
 for n,h in receipt['artifact_sha256'].items():
  if digest(run/n)!=h:raise ValueError('native member changed after report: '+n)
 print(json.dumps(dict(rendered=str(out/'report.pdf'),native_payloads_unchanged=True,curve_cell_rows=len(summary['rows']),scientific_invocations=0)))
if __name__=='__main__':main()
