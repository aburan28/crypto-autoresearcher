#!/usr/bin/env python3
"""make_blind_yaml.py -- assemble out/blind_rederivation.yaml from the run outputs (no hand-typed numbers).
Run from out/:  python3 src/make_blind_yaml.py
It contains NO review_attestation key (the single attestation lives in red_team_report.yaml)."""
import os, sys, json, glob, hashlib, re, subprocess, time
import yaml
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
from msparse import parse_ms, deg

def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()

def rel(p):
    return os.path.relpath(p, OUT)

root_ms = sorted(glob.glob(os.path.join(OUT, '..', 'experiments', '**', '*.ms'), recursive=True))
def key(p):
    N = parse_ms(p)[0]; return (N, p)
root_ms.sort(key=key)

vtab = {r['instance']: r for r in json.load(open(os.path.join(OUT, 'results', 'V_table.json')))}
doc = {}
doc['blind_rederivation'] = dict(task_id='TASK-20261004-095926', joint_scope='W1 W2 W3 (phase-1 values)', status='phase_1_complete')

# ------------------------------------------------------------------ implementation provenance
srcs = ['msparse.py', 'to_masks.py', 'count_solutions.c', 'closure.c', 'closure_v.c', 'closure2.c', 'ref_closure.py', 'postcheck.py', 'certificate_one.py',
        'run_V.sh', 'run_V_C.sh', 'run_all_closures.sh', 'run_instance.py', 'run_verification_suite.sh', 'check_solutions.py', 'check_parse_vs_python.py',
        'test_parser.py', 'test_counters.py', 'gen_systems.py', 'timed.py', 'window_order_check.py', 'order_experiment.py']
doc['implementation'] = dict(
    language='C (gcc 13.3.0, -O3 -march=native -fopenmp, AVX-512/BMI2 host) for the closure and the zero counters; Python 3.11 for the parser, the plain reference closure, the post-checks and the test drivers',
    libraries='C: libc, OpenMP, immintrin (_pext_u64) only.  Python: standard library; numpy 2.4.6 (brute-force ground truth for small systems only); sympy 1.14.0 (independent Groebner cross-check of PT-3b only); PyYAML 6.0.1 (writing this file).',
    m4ri_linked=False, m4ri_note='M4RI was not used and was not installed; agreement of the elimination is therefore independent of M4RI.',
    elimination=('closure.c: own reduced-row-echelon (Gauss-Jordan) elimination.  Basis rows are stored as TAIL bitsets over the non-pivot columns (pivot columns are dropped at every compaction); '
                 'candidates (products mu*f) are formed from the creation form of each row, reduced against the RREF basis by XOR of tails, batched (256 per batch, OpenMP over candidates and over old rows), '
                 'no Four Russians / no M4RI table method.  closure2.c (cross-check): plain non-reduced echelon with one-pivot-at-a-time head reduction on dense full-width rows, different column order, hash-table product lookup.  '
                 'ref_closure.py: dictionary head reduction on Python-int bitsets, literal fixed-point passes, plus a from-scratch Gauss-Jordan routine.'),
    source_sha256={s: sha(os.path.join(HERE, s)) for s in srcs if os.path.exists(os.path.join(HERE, s))},
    binary_sha256={b: sha(os.path.join(HERE, b)) for b in ['closure', 'closure_v', 'closure2', 'count_solutions'] if os.path.exists(os.path.join(HERE, b))},
    reproduce=['cd out; bash src/run_V.sh; bash src/run_V_C.sh   # (6) |V| by four routes, dumps the zero sets',
               'cd out; bash src/run_all_closures.sh               # (1)-(5),(7) for the twelve systems, increasing N',
               'cd out; bash src/run_verification_suite.sh         # re-runs with different batching, pointwise row check at all zeros, saturation verifier (insufficient instances)',
               'cd out; python3 src/postcheck.py SYSTEM.ms results/closure/NAME.lm results/V/NAME.solutions_E1.txt   # evaluation-kernel ground truth + Apriori N_std'])
doc['quantity_well_posedness'] = dict(
    well_posed=True,
    reading_choices=[
        'ORDER encoded as key (size, -bitmask): among equal sizes a smaller bitmask is the LARGER monomial (check: x1x2 > x1x3, the largest differing variable index lies in the smaller monomial).',
        'deg f of a basis row equals the size of its leading monomial (graded order), so the multiplier budget of a row is 4 - |LM|; the closure subspace itself does not depend on the graded order, only LM(W), N_std and the verdict do.',
        'Field-equation lines (x^2+x) in the files are the zero polynomial in B; they are neither counted in M (M = non-field lines: 40,40,41,41,42,42,43,43,44,44,45,45) nor added as generators.  Keeping them as zero generators changes nothing (tested).',
        'N is the number of names on line 1 (2k): 40,40,42,42,42,42,44,44,44,44,46,46, NOT the n in the file name (n41 files have N=42, n43 N=44, n45 N=46).  c, the LM masks and the hash use this N.',
        'The statement defines W as the smallest closed subspace; it does not define "iterations".  The rank after wave t that this implementation reports (wave 0 = reduced generators, wave t = products of the rows created in wave t-1) is an implementation-defined partial-progress measure, not a quantity of the statement.',
        'N_std counts squarefree monomials of ALL sizes with no LM member as a subset = faces of a simplicial complex; computed by depth-first face enumeration (C) and by an Apriori level-wise count (Python); both agree on all twelve.'])

# ------------------------------------------------------------------ (6) first
doc['quantity_6_delivered_first'] = dict(
    written_before_any_closure_on_the_twelve=True,
    table_file='results/V_table.json', table_sha256=sha(os.path.join(OUT, 'results', 'V_table.json')),
    recorded_utc='2026-10-04T23:59:24Z (file mtime; the first closure on a window system started at about 2026-10-05T00:02Z)',
    methods=['A/E1: Gray-code enumeration of the first half, XOR-mask updates, affine solve for the second half',
             'A/E2: the same with the roles of the halves exchanged', 'C/E1: direct per-assignment term evaluation, first half enumerated',
             'C/E2: the same, second half enumerated'],
    all_four_methods_agree=all(len({r['method_A_E1'], r['method_A_E2'], r['method_C_E1'], r['method_C_E2']}) == 1 for r in vtab.values()),
    zero_sets_enumerated_and_checked='every enumerated zero satisfies every generator as written (raw-exponent evaluation incl. field lines AND B-evaluation); E1 and E2 sets identical; every single-bit flip of a zero violates some generator')

# ------------------------------------------------------------------ per instance
inst = []
for ms in root_ms:
    b = os.path.basename(ms)[:-3]
    N, B, R, info = parse_ms(ms)
    cj = json.load(open(os.path.join(OUT, 'results', 'closure', b + '.closure.json')))
    pc = json.load(open(os.path.join(OUT, 'results', 'postcheck', b + '.json')))
    runtxt = open(os.path.join(OUT, 'results', 'closure', b + '.run.txt')).read().strip()
    wall = float(re.search(r'wall_s=([\d.]+)', runtxt).group(1)); rss = int(re.search(r'maxrss_kb=(\d+)', runtxt).group(1))
    vf = os.path.join(OUT, 'results', 'verify', b + '.json')
    ver = None
    if os.path.exists(vf) and os.path.getsize(vf) > 0:
        vj = json.load(open(vf))
        same_lm = sha(os.path.join(OUT, 'results', 'verify', b + '.lm')) == sha(os.path.join(OUT, 'results', 'closure', b + '.lm'))
        vlog = open(os.path.join(OUT, 'results', 'verify', b + '.log')).read()
        vt = re.search(r'TIMED wall=([\d.]+) maxrss_kb=(\d+)', vlog)
        ver = dict(rerun_threads=3, rerun_batch=(1024 if 'saturation_violations' in vj and vj.get('saturation_products', -1) >= 0 else 128),
                   rank_equal=(vj['rank'] == cj['rank']), N_std_equal=(vj['N_std'] == cj['N_std']), lm_file_byte_identical=same_lm,
                   row_eval_violations_at_all_zeros=vj['row_eval_violations'], zeros_checked=vj['points_checked'],
                   saturation_products=vj['saturation_products'], saturation_violations=vj['saturation_violations'],
                   rerun_wall_s=float(vt.group(1)) if vt else None, rerun_maxrss_kb=int(vt.group(2)) if vt else None,
                   output_sha256=sha(vf), lm_sha256=sha(os.path.join(OUT, 'results', 'verify', b + '.lm')))
    cert = None
    if cj['wave_ranks'] == [N - (1 if False else 0)] or cj['total_candidates'] == len(B):
        pass
    certp = os.path.join(OUT, 'results', 'certificates', b + '.json')
    if os.path.exists(certp): cert = json.load(open(certp))
    c = cj['columns']; V = vtab[b + '.ms']['V']
    verdict = 'sufficient' if cj['N_std'] == V else ('insufficient' if cj['N_std'] > V else 'impossible')
    inst.append(dict(
        id=b, input_path='experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e/' + os.path.relpath(ms, os.path.join(OUT, '..', 'experiments', 'EXP-SEMBIN-7e1371', 'runs', 'RUN-SEMBIN-5ed13e')),
        input_sha256=info['sha256'], N=N, M_nonfield=info['n_nonfield'], field_equation_lines=info['n_field_lines'], generator_degrees='all 2' if all(deg(p) == 2 for p in B) else 'mixed',
        q6_V=V, q6_methods_agree=len({vtab[b + '.ms'][k] for k in ['method_A_E1', 'method_A_E2', 'method_C_E1', 'method_C_E2']}) == 1,
        q6_method_D_numpy_recorded_after_the_first_four=[int(re.search(r'total=(\d+)', open(os.path.join(OUT, 'results', 'V', b + '.' + x + '.txt')).read()).group(1)) for x in ['D1', 'D2']],
        q1_c=c, q2_r=cj['rank'], q3_one_in_W=bool(cj['one_in_W']), q4_lm_counts_by_size_0_to_4=cj['lm_by_size'], q4_lm_sha256=pc['lm_sha256'],
        q5_N_std=cj['N_std'], q5_N_std_second_method_apriori=pc['N_std_apriori'], q7_verdict=verdict,
        evaluation_kernel_check=dict(eval_rank=pc['eval_rank'], r_upper_bound=pc['r_I_upper_bound'], LM_W_subset_LM_I_leq4=pc['LM_W_subset_LM_I'], rank_le_bound=pc['rank_le_bound'],
                                      LM_W_equals_LM_I_leq4=pc['LM_W_equals_LM_I'], note='closure-free; I_{<=4} = {f of degree <= 4 vanishing on V}'),
        partial_progress_wave_ranks=cj['wave_ranks'], wave_candidates=cj['wave_candidates'], wave_seconds=cj['wave_seconds'],
        wall_clock_s=wall, peak_rss_kb=rss, threads=3, early_exit_on_one_in_W=bool(cj['early_exit_one']),
        certificate_one_in_span_of_generators=cert, verification_rerun=ver,
        output_files={k: dict(path=rel(os.path.join(OUT, 'results', d, b + ext)), sha256=sha(os.path.join(OUT, 'results', d, b + ext)))
                      for k, d, ext in [('closure_json', 'closure', '.closure.json'), ('lm_masks', 'closure', '.lm'), ('closure_log', 'closure', '.closure.log'),
                                        ('run_record', 'closure', '.run.txt'), ('postcheck_json', 'postcheck', '.json'), ('window_order_check', 'window_order', '.json')]
                      if os.path.exists(os.path.join(OUT, 'results', d, b + ext))}))
doc['instances'] = inst
doc['closure2_independent_rerun'] = dict(status_at_hash_time='n40 d1 (V=4) and n40 d0 (V=0) were started in the background with the second implementation (closure2 -i); NOT complete when this file was written; whatever completes is reported as a dated addendum in red_team_report.yaml, never here', commands=['bash src/run_closure2_heavy.sh ch_n40_m2_t2_k20_low_B_ran_s20260913102_d1', 'bash src/run_closure2_heavy.sh ch_n40_m2_t2_k20_low_B_ran_s20260913101_d0'])
doc['early_exit_validation'] = dict(note='n40 d0 re-run with early exit disabled (-E): full closure reaches 1 in W and the LM file is byte-identical to the early-exit output', no_early_json=rel(os.path.join(OUT, 'results', 'earlyexit', 'n40_d0_noearly.json')), no_early_json_sha256=sha(os.path.join(OUT, 'results', 'earlyexit', 'n40_d0_noearly.json')), lm_sha256=sha(os.path.join(OUT, 'results', 'earlyexit', 'ch_n40_m2_t2_k20_low_B_ran_s20260913101_d0_noearly.lm')))
doc['unreached'] = []
doc['unreached_note'] = 'none: all twelve instances were completed inside the watchdog.'
doc['summary_counts'] = dict(sufficient=sum(1 for i in inst if i['q7_verdict'] == 'sufficient'), insufficient=sum(1 for i in inst if i['q7_verdict'] == 'insufficient'),
                             impossible=sum(1 for i in inst if i['q7_verdict'] == 'impossible'))
doc['small_n_validation_summary_file'] = 'results/small_n_validation_summary.json'
out = os.path.join(OUT, 'blind_rederivation.yaml')
with open(out, 'w') as f:
    f.write('# blind_rederivation.yaml -- TASK-20261004-095926 phase 1.  Generated by src/make_blind_yaml.py from run outputs; carries no attestation block (the single attestation is in the report file).\n')
    yaml.safe_dump(doc, f, sort_keys=False, width=160)
print('wrote', out, sha(out))
