#!/usr/bin/env python3
"""Write descriptive Markdown from the sealed-data arithmetic extracts."""
from pathlib import Path
import json,datetime as dt
HERE=Path(__file__).resolve().parent;D=HERE/'data'
def read(p):return json.loads((D/p).read_text())
S=read('summary.json');R=read('runtime.json')
def table(name):
    i=read(name+'-index.json');out=[]
    for part in i['parts']:
        x=read(part['path']);out.extend(dict(zip(x['columns'],row)) for row in x['rows'])
    return out
Q=table('candidate-outcomes');C=table('per-curve-costs')
METHOD=['rho_upstream_auto','rho_upstream_auto_aa','hybrid_xmod7_exact_b8_then_rho','bernstein_lange_precomp','bsgs_complete']
NAME=dict(zip(METHOD,['AutoRho','Rho A/A repeat','Candidate then rho','Bernstein–Lange precomputation','BSGS']))
start=dt.datetime.fromisoformat(R['receipt_started_at']);end=dt.datetime.fromisoformat(R['receipt_finished_at'])
def md_table(cols,rows):
    return '\n'.join(['| '+' | '.join(map(str,cols))+' |','| '+' | '.join(['---']*len(cols))+' |',*['| '+' | '.join(map(str,row))+' |' for row in rows]])+'\n'
def f(x):return 'undefined' if x is None else f'{x:.6g}'
header=f'''# Larger classical ECDLP solver-validation report

AutoRho, Bernstein–Lange and BSGS each returned checked answers for all 768 targets. The candidate-then-rho composition also solved 768/768, using {S['hybrid']['candidate_only_hits']} candidate-only answers and {S['hybrid']['fallback_invocations']} fallback answers. This observations-only report records correctness and measured cost comparisons without assigning hypothesis status. Novelty remains a separate assessment.

- Experiment: `{S['experiment_id']}`; run: `{S['run_id']}`.
- Measured source/claim commit: `{S['source_commit']}`.
- Raw records published before this report: `{S['raw_publication_commit']}`.
- Verified archive commit: `{S['archive_commit'] or 'not yet supplied; see archive record'}`.
- Workload: 48 fresh ordinary non-anomalous curves, subgroup sizes12/14/16/18 bits, six curves per size/stratum,16 uniform targets with replacement per curve:768 targets. The nested192-target core overlaps the full panel; extension576.
- Subgroup orders: {S['scope']['subgroup_order_range'][0]:,}–{S['scope']['subgroup_order_range'][1]:,}; field primes: {S['scope']['field_prime_range'][0]:,}–{S['scope']['field_prime_range'][1]:,}. Cofactor counts: `{S['scope']['cofactor_counts']}`.
- Primary preset: x-mod-7, exact public prefixes, beam8, four offset views,2,048 unlabelled training samples. This preset was chosen from earlier data, before this fresh confirmation batch. The primary constructor omits unused diagnostics; the full secondary matrix retains them.
- Named references: actual upstream AutoRho and Bernstein–Lange from cryptanalysis commit `379faa0f1e38facd9c8fdfc527f0b89518cf2e70`, plus separately named complete BSGS. Rho A/A and hybrid fallback use the same target-specific random stream and separate charged state.
- Timing: {R['receipt_started_at']} to {R['receipt_finished_at']}; derived supervisor envelope {(end-start).total_seconds():.6f} seconds, including build, controls, measurement and output checking. Module wall intervals under three-worker concurrency are descriptive.
- Compiler: `{R['compiler']}`. Exact commands and source/input/binary digests remain in the sealed raw records.
- Verification: {S['custody']['verification_case_rows_aligned']:,} candidate/final/prefix cases aligned to separately coded Jacobian verification and replay. This is implementation diversity, not an independent scientific review session.
- Custody: {S['custody']['receipt_artifacts_hash_checked']:,} receipt artifacts, {S['custody']['producer_slots_checked']:,} producer slots and all six original streams checked by hash/length; {S['custody']['occupied_producer_slots']} occupied producer slots. No sealed file was changed.
- Private synthetic scalar labels and generation seeds were not read by this analysis. Source-enforced input separation is not OS-isolated blindness.

The [earlier compiler-stopped attempt](../../../EXP-ECDLP-381959/reports/run-20261025T1906Z/HEADER.md) is reported separately. It dispatched no confirmation measurement jobs; this report covers the successful successor only.

[Report PDF](report.pdf) · [Complete observations](observations.md) · [Machine summary](data/summary.json) · [Runtime](data/runtime.json).

Editable figures are supplied as SVG/PDF pairs: [solver recovery](figures/solver-recovery.svg), [CPU costs](figures/cpu-costs.svg), [paired ratios](figures/paired-ratios.svg), [hybrid stages](figures/hybrid-stages.svg), and [execution timeline](figures/execution-timeline.svg). The small scatter offsets distinguish overlapping recorded values; they are not additional observations. `bash build.sh` rebuilds the document and figures from retained extracts and executes no EC experiment.

Rendering requires Python, NumPy, Matplotlib and PyMuPDF. Lossless PDF object compression preserves every rendered page pixel-for-pixel. Every report page and figure PDF is visually inspected before publication. All PDFs remain below64KiB; renderer caches and inspection PNGs under `.inspection/` are not publication artifacts.
'''
out=['# Recorded solver outcomes\n',
     'All requested outcomes, including misses, failures, censoring and structural NAs, remain in the sealed records. Counts below refer to public target IDs; duplicated configurations and A/A repeats are not independent curve replications.\n']
out.append(md_table(['Arm','Requested','Solved','Failed','Censored','Invalid'],[[NAME[r['method']],r['requested'],*[r['statuses'].get(k,0) for k in ['solved','failed','censored','invalid']]] for r in S['complete_arms']]))
out.append('## Primary candidate alone and explicit fallback\n')
out.append(md_table(['Panel','Bits','Targets','Candidate-only hits','Fallback calls','Hybrid statuses'],[[r['panel'],r['bits'] or 'all',r['targets'],r['candidate_only_hits'],r['fallback_used'],json.dumps(r['hybrid_statuses'],sort_keys=True)] for r in S['primary_recovery']]))
out.append('The complete hybrid is the frozen candidate followed on a miss by the named rho solver. Every fallback has the same deterministic arithmetic vector as its paired standalone rho arm. Candidate-only success is a separate field; a correct fallback answer does not establish candidate-only completeness. Primary and secondary x-mod-7/exact/beam8 lists match, so their hits must not be counted twice.\n')
out.append('## Required setup, target CPU and reuse\n')
out.append(md_table(['Arm','Setup CPU(s)','Target CPU(s)','Total CPU(s)','Aggregate ms/target'],[[NAME[r['method']],f(r['setup_cpu_seconds']),f(r['target_cpu_seconds']),f(r['setup_cpu_seconds']+r['target_cpu_seconds']),f((r['setup_cpu_seconds']+r['target_cpu_seconds'])/r['requested']*1000)] for r in S['complete_arms']]))
out.append('These are sums of recorded method setup and target intervals, not the whole study CPU. The aggregate final column is a ratio of sums. The registered paired estimator gives each curve equal weight: for each curve, divide candidate method setup-plus-target CPU by the same curve’s rho CPU, then take the geometric mean. Full-panel setup reuse is m=16. The fixed core reuses setup over m=8 on24 core curves. No secondary configuration or A/A rerun increases the number of distinct targets available for amortization.\n')
out.append('Cold-use totals are reconstructed as recorded setup plus one recorded target interval. Setup was not independently rerun cold for every target. Whole per-arm CPU captures upstream hash/table/RNG work and candidate DP/log/sort work that EC field counters do not fully describe. Timing boundaries exclude common input validation, parsing, JSON/log formatting, module orchestration and final table teardown; none is silently claimed measured inside these intervals.\n')
out.append(md_table(['Panel','Bits','Numerator/rho','Complete pairs/requested','Geometric mean','Min','Max'],[[r['panel'],r['bits'] or 'all',NAME[r['numerator']],f"{r['comparable_complete_curves']}/{r['requested_curves']}",f(r['geometric_mean']),f(r['min']),f(r['max'])] for r in S['paired_cost_ratios']]))
out.append('Additional descriptive arithmetic references the documented precomputation baseline directly; these views do not replace the registered primary hybrid/rho comparison.\n')
out.append(md_table(['Panel','Bits','Numerator/BL','Complete pairs/requested','Geometric mean','Min','Max'],[[r['panel'],r['bits'] or 'all',NAME[r['numerator']],f"{r['comparable_complete_curves']}/{r['requested_curves']}",f(r['geometric_mean']),f(r['min']),f(r['max'])] for r in S['additional_baseline_ratios']]))
out.append('A ratio below1 means less recorded CPU in that named cost regime; a ratio above1 means more. This defines the measured comparison and is not a claim about a different scale, setup-reuse count, memory regime or implementation. Invalid, censored or zero-timing pairs retain their outcomes and have no qualified complete-cost ratio. A valid-pair subset is labeled and does not erase unresolved requested pairs. Whiskers and ranges are full observed spreads, not confidence intervals.\n')
out.append('## A/A controls\n')
out.append(f"All {S['aa']['exact_seed_work_answer_pairs']} rho A/A pairs have matching seed, answer/status and complete arithmetic counter vector. Target CPU A/A/rho summary: `{json.dumps(S['aa']['target_cpu_ratio_aa_over_rho'])}`. Zero-timing cases: `{S['aa']['unresolved_zero_cpu_cases']}`. These repeats reveal slot/timing variation; they are not independent stochastic replicates or new targets. No guessed noise correction is subtracted.\n")
out.append('## Complete secondary matrix\n')
out.append(md_table(['Feature','Mode','Beam','Cases','Hits','Checks','Sum B/r'],[[r['feature'],r['mode'],r['beam'],r['cases'],r['hits'],r['checks'],f(r['uniform_guess_expected_hits'])] for r in Q if r['panel']=='full' and r['bits'] is None and r['stratum'] is None]))
out.append(f"The secondary output includes {S['rows']['kernels']} kernels, {S['rows']['secondary_targets']:,} target cases and {S['rows']['not_applicable']} explicit fifth-residue NAs. The constant feature gives no scalar information; paired constant modes can repeat the same lists. For constant guesses, B/r is an exact ideal-uniform population probability. For other features it is only a matched candidate-budget reference. The pooled union across configurations is not one decoder’s success rate.\n")
out.append('Training/heldout construction, all views and each inference/check remain in the study record. Optional diagnostics are charged study work, not primary algorithm requirements. Shared secondary views count once per feature/target; shared fixture-validation counters count once per curve, not once per kernel.\n')
out.append('## Memory, common validation and retained scope\n')
out.append(f"Common curve-plus-all16-target membership validation CPU: {S['common_public_validation']['process_cpu_seconds']:.9g}s across48 rows. It is recorded once outside the arm timers; charging its entire16-target work to a reconstructed one-target cold or eight-target core would mislabel the measurement.\n")
out.append('Memory fields are explicit kernel/vector payloads or upstream byte estimates, with omissions stated in source records. No per-arm peak RSS was measured. The12GiB setting is a declared operational envelope, not memory usage. Scalar-mul calls contain group operations; powers/inversions contain field multiplies. These nested counters are not additive primitive work.\n')
out.append(md_table(['Arm','Recorded payload/estimate min–max(bytes)','Target table estimate min–max(bytes)','Exact source scope'],[[NAME[m],f"{min(r['payload_bytes'] or 0 for r in C if r['panel']=='full' and r['method']==m):,}–{max(r['payload_bytes'] or 0 for r in C if r['panel']=='full' and r['method']==m):,}",f"{min(r['target_table_estimate_max_bytes'] for r in C if r['panel']=='full' and r['method']==m):,}–{max(r['target_table_estimate_max_bytes'] for r in C if r['panel']=='full' and r['method']==m):,}",S['memory_sources'][m]] for m in METHOD]))
out.append('The fresh data span four toy subgroup-bit sizes with48 curve replication units. Full/core panels overlap; targets/configurations share preprocessing. No bootstrap, significance test or exponent fit was registered or computed. The records support the actual checked solver outcomes and implementation comparisons at these inputs, and identify costs to address in a next revision. Novelty is a separate assessment; the report does not change hypothesis status or exhaust a mathematical family.\n')
out.append('## Raw evidence and reproducibility\n')
out.append(f"Raw publication `{S['raw_publication_commit']}` preceded analysis. Archive binding: `{S['archive_commit'] or 'pending Coordinator binding'}`. Sealed parts manifest SHA-256 `{S['custody']['parts_manifest_sha256']}`; public verification manifest `{S['custody']['verification_manifest_sha256']}`. Every producer stream reconstructs to its original byte length and SHA-256. Exact per-target lists/counters and all failed outcomes remain linked in the raw run rather than being replaced by the summaries.\n")
for a,b in [('all768','all 768'),('solved768','solved 768'),('using{','using {'),('and{','and {'),('sizes12','sizes 12'),('bits,','bits,'),(',16',', 16'),(':768',': 768'),('nested192','nested 192'),('extension576','extension 576'),('beam8','beam 8'),('views,2,048','views, 2,048'),('below64KiB','below 64KiB'),('m=8 on24','m=8 on 24'),('below1','below 1'),('above1','above 1'),('all16','all 16'),('entire16','entire 16'),('across48','across 48'),('The12GiB','The 12GiB'),('with48','with 48')]:
    header=header.replace(a,b);out=[s.replace(a,b) for s in out]
(HERE/'HEADER.md').write_text(header)
(HERE/'observations.md').write_text('\n'.join(out))
print('Wrote provenance and complete descriptive tables from retained extracts.')
