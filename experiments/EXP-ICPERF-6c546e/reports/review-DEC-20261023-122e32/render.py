from pathlib import Path
import os,json,yaml,math,statistics
os.environ.setdefault('MPLCONFIGDIR','/tmp/ic-report-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst
review=yaml.safe_load(Path('coordination/tasks/TASK-20261023-6562b0/review_report.yaml').read_text())['review_report']
m=review['recomputed_metrics'];run=Path('experiments/EXP-ICPERF-6c546e/runs/RUN-ICPERF-d566af')
raw=json.loads((run/'raw-result.json').read_text())
out=Path('experiments/EXP-ICPERF-6c546e/reports/review-DEC-20261023-122e32');out.mkdir(parents=True,exist_ok=False)
fig,ax=plt.subplots(figsize=(9.4,3),layout='constrained')
y=[0,1,2,3,4];vals=[m['per_bits'][str(b)] for b in [12,14,16]]+[m['speedup'],m['aa_factor']]
ax.scatter(vals,y,color=['#0072B2']*3+['#009E73','#777777'],s=65,zorder=4)
ax.errorbar(m['speedup'],3,xerr=[[m['speedup']-m['ci95'][0]],[m['ci95'][1]-m['speedup']]],fmt='none',capsize=5,color='#009E73',linewidth=2)
ax.axvline(1,color='#777777',linestyle=':',label='Equal time')
ax.axvline(1.05,color='#D55E00',linestyle='--',label='Frozen pooled point gate1.05')
ax.set(yticks=y,yticklabels=['12 bits;18 pairs','14 bits;18 pairs','16 bits;18 pairs','Pooled;54 pairs;9 curves','A/A label contrast;54 pairs'],xlabel='Geometric full-solve reference / candidate ratio (dimensionless)',title='RUN-ICPERF-d566af: reviewed complete-solve contrast',xlim=(.98,1.34))
ax.invert_yaxis();ax.grid(axis='x',alpha=.2);ax.legend(fontsize=8,loc='lower right')
fig.savefig(out/'measurements.svg');plt.close(fig)
md=f'''# Scoped acceptance of the balanced native target generator

Decision: DEC-20261023-122e32 accepts EV-ICPERF-92c130 as moderate empirical toy evidence for the optional native fixed-window target generator. This is a complete instrumented native solve API observation on a specified host/session. Reference defaults, official frontiers, measured bounds and hypothesis statuses do not change.

Observation: EXP-ICPERF-6c546e / RUN-ICPERF-d566af completed all162 workers,54 matched pair-repetitions,18 distinct curve/solver streams and nine new public12/14/16-bit curves. The raw snapshot is ed0d34e276149b30d137448f22b0fb17cdd4cf28; executable/input commit e9f89202f5977ad5e39cc42311cfa781a24d41f7. Parameters: curve seeds3/4/5, solver seeds0/1, three repetitions, m2/small_x/mitm, accelerate=false, harvest=off, target window4; target seed0. No missing, failed, invalid or timed-out row. All targets, relation streams and recovered logarithms match.

Comparison: within every exact curve/solver cell every arm occupies every slot once, and all six permutations occur per curve. Baseline per pair is the arithmetic mean of reference A/B. The geometric paired reference/candidate ratio is **{m['speedup']:.8f}**, against max(1.05,A/A) =1.05. A/A is{m['aa_factor']:.8f}; it is an observed geometric label contrast, not an upper noise bound. The stratified9-curve clustered bootstrap (5000 resamples, seed3065) gives95% interval **[{m['ci95'][0]:.8f},{m['ci95'][1]:.8f}]**, with sorted zero-based order statistics124/4875. The blinded independent derivation initially used floor indices124/4874 and gives upper{m['ci95_blind_floor_nminus1'][1]:.8f}; linear interpolation gives upper{m['ci95_linear_nminus1'][1]:.8f}. Frozen empirical-percentile wording did not settle endpoint rounding; all conventions and the unchanged positive gate are disclosed, not retroactively rewritten.

![Reviewed wall-time contrast and numerical gates](measurements.svg)

The pooled whisker is the curve-clustered interval; per-size and per-slot ratios are descriptive, without new significance or independent replications. Per-bit ratios12/14/16:{', '.join(f"{m['per_bits'][str(b)]:.5f}" for b in [12,14,16])}. Candidate-slot0/1/2 ratios:{', '.join(f"{m['per_candidate_slot'][str(b)]:.5f}" for b in range(3))}. Five of54 candidate pairs are slower. Full group-operation sums per54 solves are200856 reference versus50490 candidate; target-generation sums193698 versus43332 include per-solve table construction. Counts and seconds are separate units.

Inference: independent fresh xhigh TASK-20261023-6562b0 owns J-integrity and J-inference; both hold within this conditional scope. The reviewer independently rederived raw statistics before reading successor source or historical audits, preserved permanent semantic blindness to producer summaries/base analysis, and reused the prior committed unchanged-base-worker audit plus blind native algebra TASK-20261023-5301b1. It independently counted nine prime curve orders, replayed18 seeded target/relation/elimination streams and checked all162 kP=Q witnesses. Actual scratch checker controls reject the old always-middle schedule, wrong logarithm, target/config digests, missing row, wrong/missing affinity, wrong environment and missing load. Identical candidate times produce ratio1 and fail the strict gate. The exact-plan independence checker passes. Opaque protected-path hashing and imported checker execution are explicitly disclosed in the review; no protected semantic summaries were read.

The timer surrounds the entire instrumented solve API call, including factor base, decomposition and target tables, unsuccessful attempts, relations, elimination/recovery, final certificate and result construction. Trace recording is inside both arms; trace hashing, public fixture construction, startup/imports, environment/affinity/load telemetry, separate checker and supervisor are outside. Internal historical seconds_total/group_ops end before final verification and are not substituted. Setup is a subset of the relation phase and is not added twice. Driver harness40.32456s overlaps the40.64248s process and41.21535s supervisor envelope: never sum them. No separate checker phase is inferred by subtraction.

Limitation: one AMD EPYC9V74 host/session, CPython3.12.14, scalar native mitm, all workers CPU0. Nine held-out curves provide only three independent curve groups per bit stratum;54 repetitions are not54 independent curves. The interval is descriptive/conditional. The Coordinator launched no known scientific competitor during17:06:26–17:07:07UTC, but visible process/load census cannot prove host-wide or transient isolation. Lock/affinity are verified for every row. Worker peak RSS29,749,248–31,322,112 bytes includes interpreter/imports and is not an incremental memory saving;304–440-byte packed coordinate payload excludes Python overhead. Full-solve CPU observations span0.001137276–0.174347187 CPU seconds and are not added to wall time.

No production-curve, vectorized, universal per-instance, asymptotic, best-known-baseline, rho, Bernstein–Lange or attack-cost-bound conclusion follows. Matched rho/BL gaps are unmeasured. Hash-bound custody and certificates do not provide a zkVM execution proof or official ECBND measured bound. The prior confounded EXP-ICPERF-3065f9 remains preliminary and is never pooled with this run. CORR-20261023-d33e18 records its earlier sparse local lane-census limitation separately from scientific validity.

Next action: land and document the optional generator and structured claims/ic-target-balanced-6c546e.json; keep GOAL-ICPERF-e6b6a4 active. Larger/vectorized and best-known IC/rho comparisons need separately frozen prospective protocols. The original slot-confound problem is resolved only for this successor by the linked evidence. Existing canonical official ECDLP frontier/bound graphs were checked for applicability: no sealed bound or frontier transition is authorized, so no graph edge changes. Earlier experiment report graphs remain immutable. This decision adds the measured scoped graph above and the native README evidence link.

Sources: coordination/tasks/TASK-20261023-6562b0/review_report.yaml and derivation.md; prior dependency audits TASK-20261023-5301b1 and TASK-20261023-18b489; the frozen specification/trial plan, sealed run artifacts and matched structured claim. Sources are internal artifacts read by the Coordinator; no new external citation is asserted.
'''
(out/'report.md').write_text(md)
t=lambda s:json.dumps(s,ensure_ascii=False)
parts=[
f'DEC-20261023-122e32 accepts EV-ICPERF-92c130: moderate empirical, toy scope. EXP-ICPERF-6c546e / RUN-ICPERF-d566af; independent TASK-20261023-6562b0. Historical reference default unchanged.',
f'Observation:162 complete workers,54 pairs,9 unseen12/14/16-bit public curves,18 target/relation streams. Seeds3/4/5; solver seeds0/1;3 repetitions; m2/small_x/mitm, scalar, harvest off, window4. Every arm crosses every slot; all six permutations occur.',
f'Comparison: paired geometric full-solve ratio{m["speedup"]:.6f}; A/A{m["aa_factor"]:.6f}; pooled95% interval[{m["ci95"][0]:.6f},{m["ci95"][1]:.6f}],5000 stratified curve-cluster resamples. Frozen point gate1.05 and interval lower>1 pass. Blind floor upper1.197412 and linear upper1.197418 also retained; percentile rounding was unspecified. Five pairs are slower.',
'Inference: independent integrity and inference joints hold in this scope. Nine orders exhaustively counted;162 certificates and18 streams replayed. Wrong-log/config/target/row/environment/affinity/load controls and original middle-only schedule reject; identical-time gate fails. Prior blind algebra and unchanged-worker audit reused explicitly.',
'Boundary: complete instrumented native API call includes all per-solve setup, misses, relations, LA/recovery and final verification; startup/imports, fixtures, telemetry, hashing and checker excluded. Setup is not double-counted. Full group-op sums200856 versus50490 per54 solves; no addition of unlike or overlapping costs.',
'Limit: one CPython3.12.14/EPYC9V74 CPU0 host/session;9 curves, not54 independent curves. No known competing scientific producer; census cannot prove global isolation. RSS28.37–29.87MiB; packed payload304–440 bytes excludes Python objects. No default/frontier, rho/BL, deployed-curve, asymptotic or execution-proof claim.',
'Next: publish optional implementation and structured claim; keep goal active. Original confounded timing remains preliminary. Raw snapshoted0d34e276149b30d137448f22b0fb17cdd4cf28; sourcee9f89202f5977ad5e39cc42311cfa781a24d41f7. Full methods, controls, citations and limits:report.md.'
]
typ='#set page(paper: "a4", margin: 14mm)\n#set text(font: "DejaVu Sans", size: 8.5pt)\n#text(size: 16pt, weight: "bold")[Reviewed balanced index-calculus improvement]\n\n'+ '\n\n'.join('#text('+t(s)+')' for s in parts[:2])+'\n\n#image("measurements.svg", width: 100%)\n\n'+'\n\n'.join('#text('+t(s)+')' for s in parts[2:])+'\n'
(out/'report.typ').write_text(typ);(out/'render.py').write_text(Path(__file__).read_text());typst.compile(str(out/'report.typ'),output=str(out/'report.pdf'))
print(out)
