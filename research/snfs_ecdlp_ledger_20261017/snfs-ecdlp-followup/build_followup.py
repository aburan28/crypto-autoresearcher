"""Build an evidence report and corrected, gated next-stage designs."""
from pathlib import Path
import csv,json,hashlib,html,platform,statistics
ROOT=Path(__file__).resolve().parent
PREV=ROOT.parent/'snfs-ecdlp-experiments'


def main():
    blind=json.loads((ROOT/'blind-results.json').read_text())
    geo=json.loads((ROOT/'geometry-results.json').read_text())
    native=json.loads((ROOT/'norm-native-results.json').read_text())
    extended=json.loads((ROOT/'norm-extended-results.json').read_text())
    original=json.loads((PREV/'experiment-plans.json').read_text())
    dispositions=list(csv.DictReader((PREV/'all-leads.csv').open()))
    overrides={
        'SNFS-E3':('P1-gated-research','Blind degree-1 F5B recovered 4 sections and certified 5 negatives per encoding; all 9 degree-2 cases per encoding timed out at 4 seconds. Independent blind geometry found all 10 existing sections among 18 unique cases. No rho advantage shown.'),
        'SNFS-E1':('support-E3','The classical split cubic pencil supplies rank 8 through the target fibre. Further work must address rank growth, not rediscover this baseline.'),
        'SNFS-E2':('support-control','Retain the exact E8 height baseline; no new generator-height theorem inferred.'),
        'SNFS-E4':('P1-support','Measure actual coverage at the degrees used by the blind solver. N(H)>=p is only a necessary count condition.'),
        'SNFS-A3':('park-tested-norm-method','Native norm/gcd and enumeration agreed on all 672 unique instances (432 small + 240 larger). The norm method lost all native 8-target batch comparisons; largest cold ratio about 3.96. This specific m=2 method is not a promising speed lead.'),
        'SNFS-D4':('retire-original-trigger','Original smoothness/kernel independence trigger remains invalid when B<p and W is nonzero. No new evidence reopens it.')}
    for r in dispositions:
        priority,decision=overrides.get(r['provisional_id'],('archive-control-or-unresolved',r['verdict']))
        r.update(followup_priority=priority,followup_decision=decision)
    (ROOT/'all-lead-dispositions.json').write_text(json.dumps(dispositions,indent=2)+'\n')
    designs=[dict(id='E3-coverage-gate',status='proposed-not-run',provisional_ids=['SNFS-E3','SNFS-E4'],cpu_cap_hours=2,
        question='Does a structured blind solver remain competitive at degrees with substantial fresh-target coverage?',
        instances='p=257,1021,4093,16381,65537; 3 independently seeded split pencils per p; degrees 1,2,3,4 initially; 30 fresh non-base finite targets per cell. Increase degree only after an exact count/coverage screen.',
        solvers=['Blind geometric class construction with base-locus recovery charged','A sparse coefficient solver with saturation and multiple primitive charts','Known-generator lattice search as a labeled oracle control','Rho on every target'],
        measurements=['Coverage at each degree including all chart exclusions','Single-target cold and shared-precomputation batch costs','Completed recovered-log operation including preprocessing, failures, coordinate extraction and verification','Timeout-censored distributions; planted controls reported separately'],
        controls=['Workers use only surface equations and target; audit that known generator/scalar data is not referenced','Every returned section satisfies the polynomial identity and gives a verified specialization log','Matched success uses fallback rho charged for every failed section target','At least one independent surface held out per size'],
        stopping_rule='Stop a blind solver line after two cells with over 50% timeouts at a 10-second per-target cap. Do not extend the campaign unless a held-out matched-coverage comparison improves as p grows. Fixed-rank polynomial class enumeration is a control, not evidence of a new exponent.'),
        dict(id='E1-rank-growth-gate',status='proposed-not-run',provisional_ids=['SNFS-E1','SNFS-E2'],cpu_cap_hours=2,
        question='Can an explicit certified construction exceed rank 8 through prescribed generic ordinary fibres without excessive height or setup cost?',
        instances='First audit one explicit chi=2 construction at p=101,257,1021 on 10 prescribed j/twist targets per p; retain the split rank-8 pencil as control.',
        measurements=['Explicit independent sections and certified Gram determinant','Arithmetic rank versus geometric rank','Exact fibre isomorphism including twist','Construction, specialization and height costs'],
        controls=['Do not infer rank from point counts only through extension degree 10','Use a theorem with checked hypotheses, or independent sections plus a certified upper bound','Separate special-j or constant-j families from generic prescribed targets'],
        stopping_rule='Stop this construction if rank>8 through generic prescribed fibres is not certified within the cap. Do not launch a thousands-of-surfaces survey on an uncertified rank estimator.'),
        dict(id='A3-norm-stop',status='screen-completed-no-scaleup',provisional_ids=['SNFS-A3'],cpu_cap_hours=0,
        decision='Park this particular m=2 norm method. Reopen only for a distinct algorithm or cost model with a completed-operation advantage over the native baseline.',
        controls=['A native enumeration implementation and shared factor-base setup are mandatory','No exponent inferred from microsecond small-field timings','A full relation-yield and matrix-cost model is required before an index-calculus claim'])]
    nextstage=dict(scope='Gated proposals after the follow-up, not executed full campaigns.',designs=designs,
        earlier_all_23_designs='../snfs-ecdlp-experiments/experiment-plans.json',
        restrictions=original['common_protocol'],canonical_ids_assigned=False,campaign_seeds_reserved=False)
    (ROOT/'next-experiments.json').write_text(json.dumps(nextstage,indent=2)+'\n')
    native_summaries=native['summary']+extended['summary']
    summary=dict(best_lead='SNFS-E3, with E1/E2/E4 support; conditional research priority, no demonstrated attack advantage',
        prior_all_23='All 23 have finite pilots/receipts, not their original full protocols.',
        new_unique_norm_cases=672,norm_comparisons_including_backend_repeats=1104,
        E3_unique_targets=18,E3_generic_solver_runs=36,E3_generic_summary=blind['summary'],
        geometry_sat=sum(r['solver']['status']=='sat' for r in geo['rows']),geometry_cases=18,
        norm_native_summary=native_summaries,
        norm_largest_native_cold_ratio=extended['summary'][-1]['cold_norm_to_enumeration_median'],
        norm_largest_native_batch_ratio=extended['summary'][-1]['eight_target_batch_norm_to_enumeration_median'],
        no_asymptotic_claim=True,no_sieving=True,no_deployed_keys=True)
    (ROOT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    metadata=dict(python=platform.python_version(),date_utc='2026-10-17',execution='Serial bounded pilots; no remote service and no background campaign.',
        provenance=['Initial norm run used SymPy point square roots. ROOT output-path shadowing was corrected afterward and its result moved to this follow-up directory; no measured value changed.',
            'Native square-root and extended-size dispatch were added after the initial norm run. The original and native small grids use identical curve and target instances, checked by verify_followup.py.',
            'Norm scripts use no known-answer root in selection. The enumeration answer is checked only after the norm solver returns.',
            'E3 raw/jet workers are called with only p,a,b,G,R,d; the source does not reference the parent generator/target scalar data. Forked workers are not an adversarial memory-isolation mechanism.',
            'Blind geometry independently recovers all nine base points from the surface equations. All output maps and specialization logs are revalidated by the parent.',
            'Earlier 23-record evidence files and archive were left unchanged; prior-verification.json rechecks them.'],
        resources=dict(norm_initial='Finite 432-case grid, under one second measured solver-loop wall time; no process resource wrapper recorded.',
            norm_native='Finite 432-case repeated grid, under one second measured solver-loop wall time; no process resource wrapper recorded.',
            norm_extended=json.loads((ROOT/'norm-extended-resource.json').read_text()),
            blind=dict(parent_wall_seconds=blind['wall_seconds'],per_worker_wall_cap_seconds=4,per_worker_cpu_cap_seconds=6,per_worker_address_cap_gib=2),
            geometry='Finite 18-target degree-1/2 grid; no independent process resource wrapper recorded.'),
        seed_policy='Prior local seed candidates plus distinct round2 case namespaces. Campaign-wide reservation and immutable IDs remain pending on the absent harness.',
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')})
    (ROOT/'run-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (ROOT/'requirements.txt').write_text((PREV/'requirements.txt').read_text()+'python-flint==0.9.0\n')
    (ROOT/'README.txt').write_text('''Special-structure ECDLP: selective follow-up, 2026-10-17

Open report.html. summary.json, all-lead-dispositions.json and next-experiments.json
give the evidence, all-23 disposition update and unrun gated experiments.
The earlier 23-record report and corrected plans are in the sibling directory.
The original full campaigns have not been executed. No asymptotic gain is claimed.

Reproduce in Python 3.12 on Linux, from the common parent directory:
  python -m pip install --target snfs-ecdlp-experiments/vendor -r snfs-ecdlp-followup/requirements.txt
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/norm_decomposition.py
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/norm_decomposition.py flint
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/norm_decomposition.py flint extended
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/blind_sections.py
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python snfs-ecdlp-followup/geometry_sections.py
  python snfs-ecdlp-followup/verify_followup.py

Run-metadata describes actual resource limits; the extended norm wrapper recorded
48 CPU seconds. Direct CLI reproduction does not install an outer resource cap.
E3 workers always enforce their own wall, CPU and address-space limits.
Timings and timeout outcomes may vary. Compare native arithmetic, cold and shared
setup separately. The two small norm grids repeat the same instances and are not
independent scientific samples. First-round files remain immutable.
''')
    e=html.escape
    body='''<!doctype html><meta charset="utf-8"><title>ECDLP follow-up evidence</title><style>
body{font:16px/1.5 system-ui;max-width:1150px;margin:36px auto;padding:0 20px;color:#182a3a}h1{font-size:28px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px;border-bottom:1px solid #dce3e8;text-align:left}th{background:#edf3f7}.note{padding:16px;background:#fff3d6}a{color:#075ca3}</style>
<h1>Continue selectively: E3 is the remaining solver question</h1>
<p>No measured result demonstrates an advantage over rho or subexponential ECDLP. The earlier assessment covers all 23 records with bounded pilots or receipts, not the original full campaigns.</p>
<p>Keep E3 with E1/E2/E4 support on a small gated budget. Park the tested A3 norm method after the native comparison. Retire D4’s original smoothness-independence trigger.</p>
<h2>Blind section solving: 18 unique targets, 36 generic-solver runs</h2>
<p>Workers take only the cubic-pencil equation and fibre target. Degree 1/2 maps must pass a primitive resultant chart check. Known generators and planted answers are used only for validation. These are low-degree finite controls.</p>
<table><tr><th>Degree</th><th>Encoding</th><th>Cases</th><th>Outcomes</th></tr>'''
    for s in blind['summary']:body+=f"<tr><td>{s['d']}</td><td>{s['method']}</td><td>{s['cases']}</td><td>{e(str(s['statuses']))}</td></tr>"
    body+='''</table><p>The independent blind geometry control recovers the base locus from a degree-at-most-9 resultant, then builds line/conic sections. It found and fully verified all 10 existing sections among 18 cases and agreed on the 8 negatives. This is classical split-pencil geometry, not a new algorithm. Conic timeouts therefore do not establish a mathematical obstruction. The successful complete costs were slower than rho on these toy cases.</p>
<h2>A3: quadratic norm versus native enumeration</h2><p>The standard power-sum norm identity eliminated one variable. All 672 unique known-answer/fresh cases agreed with complete enumeration; the 432 small cases were also rerun with a second point-square-root backend. The table uses native point arithmetic on both algorithms. Values below 1 favor the norm solver.</p>
<table><tr><th>L</th><th>p</th><th>Fresh cases</th><th>Cold ratio</th><th>8-target shared-setup ratio</th></tr>'''
    for s in native_summaries:body+=f"<tr><td>{s['L']}</td><td>{s['p']}</td><td>{s['fresh_cases']}</td><td>{s['cold_norm_to_enumeration_median']:.2f}</td><td>{s['eight_target_batch_norm_to_enumeration_median']:.2f}</td></tr>"
    body+='''</table><p>The initial SymPy baseline exaggerated the cold speedup. With native point arithmetic, every tested 8-target batch favors enumeration; at the largest size the norm solver is 3.96 times slower cold and 10.32 times slower in the batch. This parks this particular m=2 implementation. It is not an exclusion of other factor bases or algorithms.</p>
<h2>Next gates</h2><p>First measure blind E3 costs at degrees with actual fresh-target coverage, charging preprocessing, failures, coordinate recovery and verification. Use geometric class search and known-generator search as separate controls. Extend E1 only for a certified rank-growth construction through generic prescribed fibres. Stop solver lines that fail the explicit timeout/coverage gates in next-experiments.json.</p>
<h2>All 23 records</h2><table><tr><th>Record</th><th>Current disposition</th><th>Evidence / decision</th></tr>'''
    for r in dispositions:body+=f"<tr><td>{r['provisional_id']}</td><td>{e(r['followup_priority'])}</td><td>{e(r['followup_decision'])}</td></tr>"
    body+='''</table><p class="note">Synthetic small fields only. No deployed keys and no sieving. Original theorem-closed items remain receipt-only. Local seed candidates are reproducible but unreserved against the absent campaign harness; immutable IDs have not been assigned.</p>
<p><a href="../snfs-ecdlp-experiments/report.html">Earlier all-23 report</a> · <a href="summary.json">Summary</a> · <a href="next-experiments.json">Next experiments</a> · <a href="blind-results.json">Blind data</a> · <a href="geometry-results.json">Geometry data</a> · <a href="norm-extended-results.json">Extended norm data</a> · <a href="verification.json">Verification</a> · <a href="run-metadata.json">Provenance and limits</a></p>'''
    (ROOT/'report.html').write_text(body)


if __name__=='__main__':main()
