from pathlib import Path
import json,math,hashlib,statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
root=Path.cwd(); run=root/'experiments/EXP-ICPERF-3065f9/runs/RUN-ICPERF-842b51'
out=root/'experiments/EXP-ICPERF-3065f9/reports/run-20261023T1603Z'
out.mkdir(parents=True,exist_ok=False)
raw=json.loads((run/'raw-result.json').read_text()); validation=json.loads((run/'validation.json').read_text()); summary=validation['summary']
launch=json.loads((run/'launch.json').read_text()); pairs={}
for row in raw['rows']: pairs.setdefault(row['pair'],{})[row['arm']]=row
fig,axes=plt.subplots(1,2,figsize=(10,3.3),layout='constrained')
colors={12:'#0072B2',14:'#D55E00',16:'#009E73'}
for bits in raw['config']['bits']:
 subset=[v for v in pairs.values() if v['fixed_window']['bits']==bits]
 ref=[1000*(v['reference_a']['seconds_full_solve']+v['reference_b']['seconds_full_solve'])/2 for v in subset]
 cand=[1000*v['fixed_window']['seconds_full_solve'] for v in subset]
 axes[0].scatter(ref,cand,label=f'{bits} bits; n=18',s=26,alpha=.8,color=colors[bits])
axes[0].plot([3,400],[3,400],color='#555555',linestyle='--',linewidth=1,label='Equal wall time')
axes[0].set(xscale='log',yscale='log',xlabel='Reference A/B mean, full solve (ms)',ylabel='Fixed-window full solve (ms)',title='54 paired observations; fresh processes')
axes[0].legend(fontsize=8)
for j,arm in enumerate(raw['config']['arms']):
 values=[r['peak_rss_bytes']/2**20 for r in raw['rows'] if r['arm']==arm]
 axes[1].scatter([j+(i%9-4)*.025 for i in range(len(values))],values,s=12,alpha=.45)
 axes[1].plot([j-.18,j+.18],[statistics.median(values)]*2,color='black',linewidth=2)
axes[1].set(xticks=range(3),xticklabels=['Reference A','Fixed window','Reference B'],ylabel='Worker peak RSS (MiB)',title='Measured process memory; n=54 per arm')
axes[1].grid(axis='y',alpha=.2)
fig.savefig(out/'measurements.svg')
plt.close(fig)
rows=[]
for bits in raw['config']['bits']:
 refs=[];cands=[]
 for v in pairs.values():
  if v['fixed_window']['bits']==bits:
   refs.append((v['reference_a']['seconds_full_solve']+v['reference_b']['seconds_full_solve'])/2)
   cands.append(v['fixed_window']['seconds_full_solve'])
 gm=lambda x:math.exp(sum(map(math.log,x))/len(x))
 rows.append((bits,1000*gm(refs),1000*gm(cands),gm(refs)/gm(cands)))
md='''# Fixed-base targets: recorded toy-IC run\n\nObservations only. This report records the frozen experiment and derived statistics; independent evidence review determines any claim.\n\nEXP-ICPERF-3065f9; H-ICPERF-a2284c; GOAL-ICPERF-e6b6a4. RUN-ICPERF-842b51 is archived at bc5514cf8ae037f2bd365017a94df5ede595d3e6, with explicit content custody a45755108d7d88277bba93b379515d2e78085628 (CORR-20261023-f73c58).\n\nThe supervisor launched `.venv/bin/python tools/experiment_execution.py run --plan experiments/EXP-ICPERF-3065f9/trial-plan.json --owner coordinator-ic-window --epoch 1`. Source commit: %s; bound sources were committed and unchanged at launch. The workload is nine public prime-order toy curves at 12/14/16 bits, curve seeds 0/1/2, solver seeds 0/1, target seed 0, three repetitions, m=2, small_x, mitm, scalar decomposition, harvest off, window 4. All 162 workers completed; none failed, timed out or was censored.\n\nThe external full-solve timer includes each arm's factor base, decomposition table, target-cache setup, missed decompositions, elimination and final solver verification. Public instance generation, process startup, trace hashing and independent checking are outside this timer; the driver harness timer ends before independent checking. Measured driver harness time: %.6f seconds. Wall seconds, CPU seconds and operation counts are separate units.\n\n| Field bits | Reference geometric mean (ms) | Candidate geometric mean (ms) | Derived paired ratio |\n|---|---:|---:|---:|\n'''%(launch['authority']['commit'],raw['harness_seconds'])
for bits,b,c,ratio in rows: md+=f'| {bits} | {b:.4f} | {c:.4f} | {ratio:.4f} |\n'
lo,hi=summary['clustered_bootstrap_95_interval']
md+=f'''\nAcross 54 pairs, the derived geometric paired ratio is {summary['geometric_mean_speedup']:.6f}; the predeclared clustered 95%% bootstrap interval is [{lo:.6f}, {hi:.6f}]. Each reference observation is the arithmetic mean of A and B. The A/A geometric factor is {summary['aa_factor']:.6f}. Bootstrap: 5000 resamples, seed 3065; resample three curve clusters within each bit-size stratum, retaining both solver seeds and all repetitions. The frozen numerical criterion is recorded as {summary['protocol_criterion_met']}; this is not an independent review verdict.\n\n![Recorded wall time and peak RSS](measurements.svg)\n\nThe checker independently counted curve points, checked prime field/order and every recovered kP=Q, regenerated every seeded target, and matched factor-base points/signs, target/relation digests and deterministic work counters. The known-wrong logarithm and identical-timings performance controls were rejected. All raw arm records remain in `arms.jsonl` and `raw-result.json`; validation is `validation.json`.\n\nHost: Linux 6.18.55 x86_64/glibc2.41, AMD EPYC 9V74 host, five visible logical CPUs, CPython 3.12.14, NumPy 2.3.5. Recorded load averages after the grid: {raw['environment']['load_average']}. Worker peak RSS spans 24.85–26.85 MiB across arms; packed target-coordinate payload is 304–480 bytes for the candidate and excludes Python/container overhead. The graph plots every recorded row; the horizontal marks are medians.\n\nLimits: scalar decomposition only, one host, nine toy instances. These measurements do not compare Pollard rho, vectorized decomposition, deployed curves or asymptotic exponents. No official frontier is updated; canonical frontier graphs remain unchanged. Final mathematical certificate checks do not establish a release-contract execution proof.\n'''
md=md.replace('95%%','95%')
(out/'report.md').write_text(md)
caption=f'RUN-ICPERF-842b51: 162 workers, 54 matched pairs. Derived ratio {summary["geometric_mean_speedup"]:.4f}; clustered 95% interval [{lo:.4f}, {hi:.4f}]; A/A factor {summary["aa_factor"]:.4f}.'
text=lambda v:json.dumps(v,ensure_ascii=False)
typ='''#set page(paper: "a4", margin: 14mm)\n#set text(font: "DejaVu Sans", size: 9pt)\n#text(size: 17pt, weight: "bold")[Fixed-base targets in toy index calculus]\n\nObservations only; independent evidence review determines any claim.\n\n#text(%s)\n\n#image("measurements.svg", width: 100%%)\n\n#text(%s)\n\n#text(%s)\n\n#text(%s)\n\n#text(%s)\n\n#text(%s)\n'''%(text('EXP-ICPERF-3065f9 / H-ICPERF-a2284c / GOAL-ICPERF-e6b6a4'),text(caption),text('All 162 workers completed; no failures/timeouts/censored records. Nine public prime-order curves at 12/14/16 bits; curve seeds 0/1/2, solver seeds 0/1, target seed 0, three repetitions, m2, small_x, mitm, scalar decomposition, harvest off, window 4.'),text('Timer: entire native solve, including factor base, all table setup, misses, elimination and final verification. Excludes public-instance generation, process startup, trace hashing and independent checker. Each arm pays its own setup. Wall/CPU/group operations are not summed.'),text('Independent checker: point counts and subgroup/order; recovered kP=Q; every seeded target; paired factor-base points/signs, relation digests and deterministic counters. Known-false log and zero-advantage controls rejected. Source '+launch['authority']['commit']+'. Launch source files unchanged. Command and raw receipts are in the run directory; detailed source/provenance is in report.md.'),text('Limits: one host; scalar-decomposition toy workload. Candidate remains optional. No vectorized/default-pipeline, Pollard-rho, deployed-curve, asymptotic or official-frontier claim. Process peak RSS includes Python overhead; coordinate payload 304–480 bytes does not. CPython 3.12.14, NumPy 2.3.5, Linux x86_64, five visible CPUs on AMD EPYC 9V74.'))
(out/'report.typ').write_text(typ)
(out/'render.py').write_text(Path(__file__).read_text())
typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
print(out)
