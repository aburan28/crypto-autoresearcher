"""Render only archived observations; no experiment or solver is invoked."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
RUN=HERE.parents[1]/'runs'/'RUN-PFIVE-c8c614'
read=lambda name:json.loads((RUN/name).read_text())
geo,sat,receipt,launch,env=(read(n) for n in ('geometry.json','sat.json','execution-receipt.json','launch.json','environment.json'))
inverse=[c for c in geo['graeffe']['cells'] if c['kind']=='inverse']
labels=[f"p={c['input']['p']}, d={c['input']['d']}" for c in inverse]
fig,axes=plt.subplots(1,2,figsize=(9,3.4))
x=range(len(inverse))
axes[0].bar([i-.18 for i in x],[len(c['inverse']['relations']['graeffe']) for c in inverse],.36,label='Graeffe: repetitions allowed')
axes[0].bar([i+.18 for i in x],[len(c['inverse']['relations']['quotient']) for c in inverse],.36,label='Quotient: squarefree')
axes[0].set_xticks(list(x),labels);axes[0].set_ylabel('Relations (exact count)');axes[0].legend(fontsize=7)
statuses=[sum(r['learner']['status']==s for r in sat['rows']) for s in ('sat','unsat')]
axes[1].bar(['Residual/membership SAT','Residual/membership UNSAT'],statuses,color=['#267a8e','#60758a'])
axes[1].tick_params(axis='x',labelsize=8);axes[1].set_ylabel('Original solver cells (count)')
fig.suptitle('RUN-PFIVE-c8c614: retained completed producer outputs')
fig.tight_layout();fig.savefig(HERE/'observations.svg');plt.close(fig)
clauses=sum(len(r['learner']['learned']) for r in sat['rows'])
early=sum(len(c['prefix'])<2*r['instance']['s'] for r in sat['rows'] for c in r['learner']['learned'])
paragraphs=[
'Observations only. This report covers an interrupted local experiment and does not adjudicate any hypothesis. Completed producer outputs survived; the original native independent check did not run. A failed or interrupted process is not a mathematical refutation.',
'Experiment EXP-PFIVE-3ca920; hypothesis H-PFIVE-6510c2; goal GOAL-PFDR-fd09e0. One native trial was requested and launched. Its terminal status is interrupted. Geometry and SAT payloads completed; algebra has no durable completed payload. Console progress is not an algebra result.',
f"The two inverse coefficient searches each exhaust 17^4 = 83,521 assignments. Their Graeffe relation counts are {len(inverse[0]['inverse']['relations']['graeffe'])} and {len(inverse[1]['inverse']['relations']['graeffe'])}; squarefree quotient counts are {len(inverse[0]['inverse']['relations']['quotient'])} and {len(inverse[1]['inverse']['relations']['quotient'])}. The predicates differ in repeated-root coverage; these counts do not measure a speed or yield advantage.",
f"The original SAT payload contains {len(sat['rows'])} cells: {statuses[0]} SAT and {statuses[1]} UNSAT. It records {clauses} learned clauses, {early} from prefixes shorter than a full assignment. All three SAT results use targets without rational curve lifts; they are not point decompositions. The cvc5 native finite-field backend is unsupported because this build lacks CoCoA.",
'The geometry payload also contains 429 complete ordered group-pair checks and 17 symbolic saturation cells. Producer checks report no mismatches. Saturated output basis degrees are smaller in these tiny fixtures, but neither solving degree nor degree of regularity was measured.',
'The original export preserves all eight aggregate arms as not completed because the native checker did not finish. The corrective experiment EXP-PFIVE-e26798 binds and independently rechecks these original payloads; it does not rewrite this interrupted record.',
]
metadata=[
f"Started {receipt['started_at']}; finished {receipt['finished_at']}. Derived elapsed duration is available from these timestamps but is not a benchmark. CPU time, peak memory and host-isolated timing were not recorded.",
f"Code authority {env['commit']}; platform {env['platform']}; Python {env['python']}. Dirty-tree state and detailed CPU host identity were not recorded by the native environment payload. Instrument source hashes are retained there.",
'Exact argv: '+json.dumps(launch['argv']),
'Fixed inputs: geometry primes 17,97,193,257 and declared cosets; SAT primes17,97,257, digit widths2,3, targets0,1,2 and both membership arms; algebra planned78 fixtures. Seed17; fixed deterministic ordering. Source/config hashes, controls and bounds are in protocol.json and config.json.',
'The operational interruption followed slow repeated monomial-order construction in eight-variable elimination. A new experiment preserves all78 algebra fixtures, caches an exhaustively equivalent ordering and saves every cell. A source-checker stale-iterator defect was found by static review before the new experiment froze and corrected additively. No before/after timing claim is made.',
'A/A, known SAT/UNSAT and corrupted-certificate controls exist in the retained producer payloads; the original umbrella independent checker has no output. Missing independent verification at this run is explicit. Exact finite counts have no sampling uncertainty; no population extrapolation is made.',
'Canonical graph review: the proposal report and knowledge/frontiers/ecdlp were considered. No hypothesis status or frontier changes are justified by this interrupted run, so canonical graphs remain unchanged. This new graph is an observational view only.',
'Evidence: ../../runs/RUN-PFIVE-c8c614/{geometry.json,sat.json,raw-result.json,execution-receipt.json,environment.json,launch.json}; ../../protocol.json; export.json. Native receipt artifact hashes bind the archived payloads. Raw archive commit ba3febcbc1 preceded this report.',
]
md='# Interrupted first attempt: five prime-field leads\n\n'+'\n\n'.join(paragraphs)+'\n\n![Recorded observations](observations.svg)\n\n'+'\n\n'.join(metadata)+'\n'
(HERE/'report.md').write_text(md)
q=lambda s:json.dumps(s,ensure_ascii=False)
src='#set page(paper: "a4", margin: 18mm)\n#set text(size: 10pt)\n#set par(justify: false)\n'
src+='= Interrupted first attempt\n'
for p in paragraphs:src+='#text('+q(p)+')\n\n'
src+='#figure(image("observations.svg", width: 100%), caption: [Exact retained counts. Two inverse cells and36 SAT cells; RUN-PFIVE-c8c614. Distinct membership predicates; no performance comparison.])\n#pagebreak()\n= Provenance and limits\n'
for p in metadata:src+='#text('+q(p)+')\n\n'
(HERE/'report.typ').write_text(src)
typst.compile(str(HERE/'report.typ'),output=str(HERE/'report.pdf'),root=str(ROOT))
print(HERE/'report.pdf')
