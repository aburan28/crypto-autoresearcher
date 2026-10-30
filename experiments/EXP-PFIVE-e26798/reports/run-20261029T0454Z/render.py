"""Derive the final report from sealed data only; never invoke a solver."""
import collections
import datetime
import json
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import typst

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT/'tools'))
import artifact_store as store
RUN=HERE.parents[1]/'runs'/'RUN-PFIVE-e793f3'
OLD=ROOT/'experiments/EXP-PFIVE-3ca920/runs/RUN-PFIVE-c8c614'
read=lambda name:store.read_json(RUN/name)
receipt=read('execution-receipt.json')
if receipt['status']!='output_validated' or receipt['check_returncode']!=0:
    raise ValueError('This completed-result report requires the native validation receipt')
checked=next(json.loads(line) for line in store.read_text(RUN/'check.stdout.log').splitlines()
             if line.startswith('{') and '"packages"' in line and '"valid"' in line)
assert checked['valid']
alg,point,launch,env=(read(n) for n in ('algebra.json','point.json','launch.json','environment.json'))
runtime=json.loads((HERE/'runtime-observation.json').read_text())
geo=store.read_json(OLD/'geometry.json')
ordinary=[c for c in alg['cells'] if c['population']=='s3_residual']
null=[c for c in alg['cells'] if c['population']=='matched_support_null']
matrix_names=['full_total','partial_total','full_block','partial_block']
backdoor_names=['fixed_block','random','min_fill','degree_drop']
matrix=[]
for name in matrix_names:
    arms=[next(a for a in c['lead3'] if a['arm']==name) for c in ordinary]
    matrix.append({'arm':name,'cells':len(arms),'statuses':dict(collections.Counter(a['status'] for a in arms)),
                   'rows_generated':sum(a['metrics']['rows_generated'] for a in arms),
                   'counted_field_ops_subset':sum(a['metrics']['all_counted_field_ops'] for a in arms),
                   'generated_matrix_entries':sum(a['metrics']['generated_matrix_entries'] for a in arms)})
backdoors=[]
for n in sorted({c['n'] for c in ordinary}):
    for name in backdoor_names:
        arms=[next(a for a in c['lead4'] if a['arm']==name) for c in ordinary if c['n']==n]
        backdoors.append({'n':n,'arm':name,'cells':len(arms),'strong':sum(a['strong_backdoor'] for a in arms),
                         'unknown_branches':sum(b['status']=='UNKNOWN' for a in arms for b in a['branches'])})
points=[]
for c in point['curve_packages']:
    rows=[r for r in c['sat_payload']['rows'] if r['instance']['curve_membership']]
    points.append({'p':c['p'],'a':c['curve']['a'],'b':c['curve']['b'],'order':c['curve']['order'],
                   'targets':len(c['targets']),'sat':sum(r['learner']['status']=='sat' for r in rows),
                   'unsat':sum(r['learner']['status']=='unsat' for r in rows),
                   'all_target_cells':len(c['sat_payload']['rows'])})
paired={}
for full,partial in [('full_total','partial_total'),('full_block','partial_block')]:
    counts=collections.Counter()
    for c in ordinary:
        a=next(a for a in c['lead3'] if a['arm']==full);b=next(a for a in c['lead3'] if a['arm']==partial)
        for key in ('rows_generated','all_counted_field_ops'):
            av,bv=a['metrics'][key],b['metrics'][key]
            counts[key+('_lower' if bv<av else '_equal' if bv==av else '_higher')]+=1
    paired[partial+'_vs_'+full]=dict(counts)
summary={'schema':'prime-five-report-observations/v1','run_id':RUN.name,'native_status':receipt['status'],
         'independent_checks':checked,'matrix_ordinary':matrix,'backdoor_ordinary':backdoors,
         'point_targets':points,'paired_instrument_counts':paired,
         'ordinary_cells':len(ordinary),'matched_null_cells':len(null),
         'all_lead3_statuses':dict(collections.Counter(a['status'] for c in alg['cells'] for a in c['lead3'])),
         'all_lead4_statuses':dict(collections.Counter(a['status'] for c in alg['cells'] for a in c['lead4']))}
(HERE/'observations.json').write_text(json.dumps(summary,indent=2)+'\n')

fig,axes=plt.subplots(1,2,figsize=(10,3.6))
labels=['Full total','Partial total','Full block','Partial block']
axes[0].bar(labels,[r['rows_generated'] for r in matrix],color='#267a8e')
axes[0].set_ylabel('Generated rows (sum over 36 ordinary cells)')
axes[0].tick_params(axis='x',labelrotation=20,labelsize=8)
for i,name in enumerate(backdoor_names):
    vals=[r for r in backdoors if r['arm']==name]
    axes[1].bar([r['n']+(i-1.5)*.17 for r in vals],[r['strong'] for r in vals],width=.17,label=name.replace('_',' '))
axes[1].set_xticks([4,6,8]);axes[1].set_xlabel('Boolean variables');axes[1].set_ylabel('Certified strong cuts (12 cells per width)')
axes[1].legend(fontsize=7);axes[1].set_ylim(0,13)
fig.suptitle('RUN-PFIVE-e793f3: bounded matrix and strong-backdoor observations')
fig.tight_layout();fig.savefig(HERE/'algebra.svg');plt.close(fig)

fig,axes=plt.subplots(1,2,figsize=(10,3.6))
axes[0].bar([str(r['p']) for r in points],[r['sat'] for r in points],label='Actual point witnesses',color='#267a8e')
axes[0].bar([str(r['p']) for r in points],[r['unsat'] for r in points],bottom=[r['sat'] for r in points],label='No decomposition in fixed base',color='#9caab5')
axes[0].set_xlabel('Prime field p');axes[0].set_ylabel('All affine target coordinates (count)');axes[0].legend(fontsize=7)
sat_cells=geo['saturation']['cells'];family_labels=[];before=[];after=[]
for c in sat_cells:
    sy=c['symbolic_cells'];family_labels.append(f"p{c['input']['p']},b{c['input']['b']}\n(n={len(sy)})")
    arm_names=list(sy[0]['arms'])
    u=next(n for n in arm_names if 'unsaturated' in n)
    s=next(n for n in arm_names if 'cert' in n)
    before.append(max(x['arms'][u]['output_max_total_degree'] for x in sy))
    after.append(max(x['arms'][s]['output_max_total_degree'] for x in sy))
axes[1].bar([i-.18 for i in range(4)],before,.36,label='Unsaturated output',color='#9caab5')
axes[1].bar([i+.18 for i in range(4)],after,.36,label='Saturated output',color='#267a8e')
axes[1].set_xticks(range(4),family_labels);axes[1].set_ylabel('Output basis degree; NOT solving degree');axes[1].legend(fontsize=7)
fig.suptitle('Actual point validation and independently rechecked original chart observations')
fig.tight_layout();fig.savefig(HERE/'points-and-charts.svg');plt.close(fig)

paragraphs=[
'Observations only. This report records finite implementation tests and independent certificate/model checks. It does not promote a hypothesis, establish a degree-of-regularity reduction, or claim an ECDLP speedup.',
f"EXP-PFIVE-e26798; H-PFIVE-6510c2; GOAL-PFDR-fd09e0. One requested native trial, RUN-PFIVE-e793f3, completed with status {receipt['status']}, process return {receipt['returncode']} and checker return {receipt['check_returncode']}. The first attempt RUN-PFIVE-c8c614 remains interrupted, with its completed geometry/SAT rechecked here as immutable inputs.",
f"Lead 1, coefficient membership: two genuine inverse searches each enumerate 17^4=83,521 assignments. Graeffe gives 53 and 472 relations with repetitions allowed; squarefree quotient membership gives 2 and 88. Independent oracle agreement holds for each predicate. These distinct predicates and exhaustive loops establish exact finite model sets, not early pruning or faster relation generation.",
f"Lead 2, certified SAT: all 106 residual/membership cells across 53 valid target coordinates were independently checked. The membership arms yield {sum(p['sat'] for p in points)} actual point witnesses and {sum(p['unsat'] for p in points)} factor-base UNSAT targets. Curves are y^2=x^3+2x+2 over F_17 of order 19 and y^2=x^3+x+4 over F_97 of order 89. All domain point pairs are checked independently, including doubling and identity handling.",
f"Lead 3, partial and block-filtered matrices: all 78 fixtures contain 390 matrix arms. Ordinary residual fixtures number {len(ordinary)}, with {len(null)} matched-support null fixtures and 6 controls. Matrix statuses across all arms: {summary['all_lead3_statuses']}. Every retained basis row carries an original-equation certificate. Both partial variants generated the same number of rows as their full counterpart in all 36 ordinary cells. Their counted field-operation subset was higher in 24 and equal in 12; neither reduced these counters. The Boolean quotient and differing filtrations do not identify intrinsic regularity.",
f"Lead 4, public-syntax strong backdoors: all 390 arms and 1,560 branch assignments were retained. Aggregate statuses: {summary['all_lead4_statuses']}. Every branch must finish for a strong-cut certificate; any UNKNOWN leaves the cut unproved. Each of the four policies certified all 12 four-variable cells but none of the 12 six-variable or 12 eight-variable cells. Every branch at those larger widths remained UNKNOWN under the fixed residual cap. Selection uses syntax/public hash order and never a witness or solution oracle.",
'Lead 5, complete charts: independent verification covers 429 ordered group pairs and 17 symbolic saturation cells. Artificial cleared-denominator slope components are removed from the generic chart, and exceptional additions are handled separately. The observed output basis degree changes are 7 to 2 or 3 and 11 to 5 or 6. They are not solving-degree or regularity measurements.',
]
limits=[
'Additional exact derivation: for a nonsingular short Weierstrass curve in characteristic greater than three and a fixed rational target R=(r,s) with s nonzero, S3(x1,x2,r)=0 already guarantees rational summand lifts. The explicit formula lambda=(x1*x2-r*(x1+x2)-2*r*r-a)/(2*s), yi=lambda*(xi-r)-s removes square-root extraction. Two denominator-cleared polynomial identities were checked exactly with SymPy, separately from the frozen trial. See two-summand-lift-lemma.md and lift-identity-check.json. An equivalent lift uses two quadratic equations: lambda^2=x1+x2+r and 2*s*lambda=x1*x2-r*(x1+x2)-2*r*r-a, with one extra field variable. This concerns projected model sets; sign/subgroup restrictions remain, and no lower regularity or faster solver follows. The implication fails for two-torsion targets and for three summands in general.',
'Custody status: raw bytes are published through the repository artifact store with independent HEAD/GET/hash readback receipts. The native snapshot verifier does not yet resolve .artifacts.json manifests, so the snapshot/review dependency chain remains incomplete. See problems/native-snapshot-artifact-manifest-resolution.md and coordination/prime_sat_five_tests_20261029/transport/. This is a metadata integration gap, not a failed mathematical check.',
'The matrix experiment implements selected Boolean monomial spans and block filtrations. Four homogeneous calibration matrices follow the author construction, but neither the full rank predictor from Smoothing the degree of regularity nor published Multi-homogeneous XL is implemented. The current public MinRankSolver targets GF(16), so applying it here would require a field port and a valid model transformation.',
'The finite-field SAT loop is a sound bounded stored-row polynomial-calculus strategy. It is not complete degree-D proof search. PySAT and Z3 results were checked; cvc5 native finite fields remain explicitly unsupported because the installed build lacks CoCoA. A/A, affine SAT/UNSAT, planted gate and deliberate certificate corruption controls were checked.',
'Four-variable backdoor successes leave only two variables after the cut, within the residual enumeration allowance. Such successes alone do not demonstrate special elliptic-curve structure. All six- and eight-variable outcomes remain visible, including UNKNOWN branches.',
'Counted field operations cover the declared instrumented subset. They exclude some inverse, evaluation, restriction and extraction costs; generated rows, matrix entries and those counters are observations of these programs. None is a complete end-to-end cost or a cryptographic-scale result. Exact enumerations have no sampling uncertainty; transfer beyond these parameters is unmeasured.',
'The experiment was designed after seeing the original residual SAT gap and operational interruption. It is not a performance holdout. All 78 original algebra fixtures were preserved. The order cache checks all 65,536 monomial comparisons; the independent source-rank checker repairs a stale-row iteration defect and passes six integrity regressions. A concurrent review added exact oracle-count and curve-selection checks before freeze.',
'The run has independent mathematical checkers, but no independent scientific adjudication or official hypothesis transition has been recorded. Canonical frontier graphs remain unchanged because this report makes no frontier claim. The displayed graphs are derived from the immutable payloads only.',
]
provenance=[
f"Frozen protocol 50187fcbb072d8b7483ae5410114e702dd2bdd4234306c362d04be556324dde0 at 04:51:26Z on 2026-10-29; source commit f1f876f25c8554ebd13fe0e260fa9ca0fb2ee8d8. Native authority commit {env['commit']}. Every source and input digest is retained in protocol.json, trial-plan.json and environment.json.",
f"Started {receipt['started_at']}; finished {receipt['finished_at']}. The timestamp difference describes elapsed execution only, with no timing comparison. Host platform {env['platform']}; interpreter {env['python']}. The native environment does not record dirty-tree state, CPU identity, CPU time or measured peak memory. CPU identity was observed separately below; the other fields remain unavailable. Runtime caps were 4 GiB and 7,200 seconds.",
f"Additive same-host observation at {runtime['recorded_at']}: {runtime['cpu_model']}, {runtime['logical_cpus']} logical CPUs, dependencies {runtime['dependencies']}. This was recorded while the algebra producer was active and is not a native launch attestation. See runtime-observation.json.",
'Exact argv: '+json.dumps(launch['argv']),
'Reproduction: hydrate policy-managed artifacts with tools/artifacts/artifacts.py pull on this run directory, then use the frozen Python environment and corrective_driver.py --verify <run>/raw-result.json. The native check log already records the completed independent check; rerunning a producer requires a new admitted run record.',
'Evidence: ../../runs/RUN-PFIVE-e793f3/{raw-result.json,point.json,algebra.json,execution-receipt.json,check.stdout.log,environment.json,launch.json}, all 78 cell checkpoints, ../../protocol.json and export.json. The export includes all original retained input files and binds stored-byte hashes. Storage publication may use .artifacts.json while retaining receipt-bound hydrated files; sealed receipts are never rewritten.',
'Primary literature checked 2026-10-29: https://eprint.iacr.org/2026/408 and https://github.com/LarsMath/monomial-of-regularity; https://eprint.iacr.org/2025/2060 and https://github.com/kcning/MinRankSolver. The two-summand derivation uses the summation-polynomial property in Proposition 2.1 of https://arxiv.org/html/1503.08001 (HTML inspected). Abstract/author-source review for the regularity papers only; the full 408 PDF was inaccessible with HTTP 403. No unavailable theorem is treated as reproduced.',
]
tables='| Matrix arm | Cells | Rows generated | Counted field operations (subset) |\n|---|---:|---:|---:|\n'+''.join(f"| {r['arm']} | {r['cells']} | {r['rows_generated']} | {r['counted_field_ops_subset']} |\n" for r in matrix)
md='# Five prime-field leads: completed finite tests\n\n'+'\n\n'.join(paragraphs)+'\n\n'+tables+'\n\n![Algebra observations](algebra.svg)\n\n![Points and charts](points-and-charts.svg)\n\n'+'\n\n'.join(limits+provenance)+'\n'
(HERE/'report.md').write_text(md)
q=lambda x:json.dumps(x,ensure_ascii=False)
src='#set page(paper: "a4", margin: 17mm)\n#set text(size: 9.5pt)\n#set par(justify: false)\n= Five prime-field leads\n'
for p in paragraphs:src+='#text('+q(p)+')\n\n'
src+='#pagebreak()\n= Recorded finite observations\n#figure(image("algebra.svg", width: 100%), caption: [RUN-PFIVE-e793f3; 36 ordinary residual cells. Strong-cut counts have 12 cells per width and policy. All counts exact.])\n'
src+='#figure(image("points-and-charts.svg", width: 100%), caption: [53 target coordinates in the new run; 17 symbolic cells from independently rechecked RUN-PFIVE-c8c614. Output basis degree is not solving degree.])\n'
for r in matrix:src+='#text('+q(f"{r['arm']}: {r['rows_generated']} generated rows; {r['counted_field_ops_subset']} counted field operations (declared subset).")+')\n\n'
src+='#pagebreak()\n= Scope and provenance\n'
for p in limits+provenance:src+='#text('+q(p)+')\n\n'
(HERE/'report.typ').write_text(src)
typst.compile(str(HERE/'report.typ'),output=str(HERE/'report.pdf'),root=str(ROOT))
print(json.dumps(summary,indent=2))
