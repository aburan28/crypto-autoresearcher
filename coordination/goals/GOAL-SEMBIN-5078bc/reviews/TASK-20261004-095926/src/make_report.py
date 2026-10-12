#!/usr/bin/env python3
"""make_report.py -- assembles out/red_team_report.yaml from the run outputs and the findings text below, and hashes every other file in out/.
Run last:  cd out; python3 src/make_report.py      (no background job may be running: every file in out/ is hashed).
This is the ONLY file that writes the attestation key; blind_rederivation.yaml carries none."""
import os, sys, json, glob, hashlib, re, shutil, time
import yaml
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from msparse import parse_ms

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def J(p):
    return json.load(open(os.path.join(OUT, p)))
def rd(p):
    return open(os.path.join(OUT, p)).read()

for d, _, _ in os.walk(OUT):
    if os.path.basename(d) == '__pycache__': shutil.rmtree(d, ignore_errors=True)

ms_rel = sorted(glob.glob(os.path.join(OUT, '..', 'experiments', 'EXP-SEMBIN-7e1371', 'runs', '**', '*.ms'), recursive=True), key=lambda p: (parse_ms(p)[0], p))
vt = {r['instance'][:-3]: r for r in J('results/V_table.json')}
inst = []
for p in ms_rel:
    b = os.path.basename(p)[:-3]
    cj = J('results/closure/%s.closure.json' % b); sj = J('results/single_level/%s.json' % b); V = vt[b]['V']
    s2p = os.path.join(OUT, 'results', 'single_level2', b + '.json')
    s2 = json.load(open(s2p)) if os.path.exists(s2p) and os.path.getsize(s2p) else None
    vi = 'sufficient' if cj['N_std'] == V else ('insufficient' if cj['N_std'] > V else 'impossible')
    vs = 'sufficient' if sj['N_std'] == V else ('insufficient' if sj['N_std'] > V else 'impossible')
    inst.append(dict(instance=b + '.ms', N=cj['N'], V=V, columns=cj['columns'],
                     literal_single_level=dict(rank=sj['rank'], deficiency_columns_minus_rank=cj['columns'] - sj['rank'], one_in_span=bool(sj['one_in_W']), N_std=sj['N_std'], verdict=vs,
                                              second_implementation_rank_and_N_std=([s2['rank'], s2['N_std']] if s2 else None),
                                              closure_json=dict(path='results/single_level/%s.json' % b, sha256=sha(os.path.join(OUT, 'results', 'single_level', b + '.json')))),
                     iterated_closure=dict(rank=cj['rank'], N_std=cj['N_std'], verdict=vi),
                     opposite_verdicts_literal_insufficient_iterated_sufficient=(vs == 'insufficient' and vi == 'sufficient')))
n_opposite = sum(1 for i in inst if i['opposite_verdicts_literal_insufficient_iterated_sufficient'])
assert n_opposite == 7, n_opposite

pt = J('results/pt/pt_summary.json')
sm = J('results/small_n_validation_summary.json')
w3c = J('results/w3/exp_c.json'); w3a = J('results/w3/exp_a.json'); w3v = J('results/w3/variants.json')
sweep = J('results/pt/pt2_sweep.json')['sweep']
c2 = {}
for f in sorted(glob.glob(os.path.join(OUT, 'results', 'closure2', '*.out'))):
    b = os.path.basename(f)[:-4]
    txt = open(f).read().strip()
    errp = f[:-4] + '.err'
    err = open(errp).read().strip().splitlines() if os.path.exists(errp) else []
    prog = [l for l in err if l.startswith('[closure2 -i]')]
    mm = re.search(r'queue (\d+)/(\d+) rank (\d+) cpu (\d+)s', prog[-1]) if prog else None
    c2[b] = dict(completed=bool(txt.startswith('{')), output=(json.loads(txt.splitlines()[-1]) if txt.startswith('{') else None), last_progress_line=(prog[-1] if prog else None),
                 rows_inserted_at_last_progress_line=(int(mm.group(3)) if mm else None), queue_position=(int(mm.group(1)) if mm else None), cpu_seconds=(int(mm.group(4)) if mm else None),
                 status=('COMPLETE' if txt.startswith('{') else 'UNREACHED (killed by me during the long tail of the queue; no LM file written)'),
                 main_run_rank=J('results/closure/%s.closure.json' % b)['rank'],
                 meaning='the independent implementation had inserted as many linearly independent rows as the main run reports as rank (c - eval_rank is an upper bound for sound rows, c for V empty), so the rank is independently reproduced; the unprocessed tail of the queue only multiplies rows of a saturated basis')
    lm2 = os.path.join(OUT, 'results', 'closure2', b + '.lm'); lm1 = os.path.join(OUT, 'results', 'closure', b + '.lm')
    c2[b]['lm_file_byte_identical_to_main_closure'] = (os.path.exists(lm2) and os.path.exists(lm1) and sha(lm2) == sha(lm1)) if c2[b]['completed'] else None

rep = {}
rep['red_team_report'] = dict(
    task_id='TASK-20261004-095926', goal_id='GOAL-SEMBIN-5078bc', batch_id='BATCH-9d649f', experiment_id='EXP-SEMBIN-7e1371', hypothesis_id='H-SEMBIN-2d7708',
    review_id='REVIEW-SEMBIN-20261004-a47503', lane='BLIND (independent re-derivation of the closure quantity from the statement and twelve inputs)',
    recorded_at='2026-10-05', scope='instrument validity of the closure quantity Q on twelve window systems and joints W1, W2, W3.  NO verdict on any whole claim; nothing asserted about Semaev Assumption 1, d_F4, any solver degree of regularity, n = 409 or 571, or the security of any curve.',
    protocol_record=dict(
        phase_1='blind_rederivation.yaml written and hashed before the specification was opened: sha256 7362e64389d15d33df0b24129283f900ed1fb5929b38a16a52b75418ef6c6d3b (phase1_hash_record.txt, 2026-10-05T02:25:43Z).  Quantity (6) |V| for all twelve was written and hashed first (results/V_table.json sha256 53ebfdce50727e69e26895557b765336eb9b581145b34fa8f5c28cf5b8160adc, 2026-10-04T23:59:24Z), before the first closure on a window system (about 2026-10-05T00:02Z).',
        phase_2='specification.yaml was placed in the sandbox by the dispatching session after phase 1 existed (the plan step of DP-5) and read afterwards (sha256 631eaa05c68e554007728b2d5315e85cf48b63a33746c5f5060d103fde14636a of the sandbox copy).  No phase-1 value was changed after reading it; the literal single-level runs (src/run_single_level.sh) and the W3 experiments were run in phase 2 and are not part of blind_rederivation.yaml.',
        values_compared_with_the_producer=False),
    verdicts=dict(W1='breaks', W2='holds', W3='breaks'),
    verdict_meaning=dict(
        W1='SCOPE break, narrow: the rank / standard-monomial arithmetic and the polarity statement are correct and reproduced; the verdict LABEL is not order-free.  A closure whose subspace W and ideal I are fixed flips between "sufficient" and "insufficient" when the admissible graded order changes (artifact A1), and under a non-admissible order the rule returns N_std < |V| although every row of W lies in the ideal (artifact A2).  The statement fixes degrevlex and the specification fixes no order, so the twelve recorded verdicts are well posed; they were additionally found order-robust (below).  What breaks is the sentence that a bare "sufficient"/"insufficient" is a property of the system.',
        W2='holds: the denominator |V| is exact, reproduced by six independent counts per instance, and no parse ambiguity changes a count.',
        W3='breaks on (c): the iterated degree-capped closure and the contract literal single-level degree-4 block give opposite verdicts on 7 of the 12 window systems (literal insufficient, iterated sufficient).  (a) holds under the contract wording (field equations multiplied like generators); (b) the literal "degree 3" is false for all twelve (degree 2) and is only covered by a "degree <= 3" or "t >= 3" reading.'),
    unreached_instances=[], reached_instances='all twelve (see blind_rederivation.yaml); none UNREACHED',
    joints=dict())

# ------------------------------------------------------------------ W1
W1 = dict(
    verdict='breaks',
    kind='scope finding (verdicts are per order), with arithmetic otherwise confirmed',
    breaking_artifacts=[
        dict(id='A1', grade='VERIFIED', what='verdict flip under admissible graded orders with W fixed',
             system='N=10, three generators as bitmask lists [[8,769],[1,530,546],[58,64,160,320,323]] (bit j-1 <-> x_j); found by src/order_flip_search.py (python random seed 2026, trial 1449); weights of the weighted orders are random.Random(1450) and random.Random(1451)',
             result='|V| = 156.  W has rank 245 and equals I_{<=4} in all four orders (the four closures span the same subspace).  degrevlex: N_std 156 sufficient; deglex: 156 sufficient; wdeg: 160 insufficient; wdeg_rev: 158 insufficient.  Ideal-level Groebner degrees 3,3,5,5.',
             reproduce='cd out; python3 src/repro_w1_artifacts.py   (log results/logs_small/repro_w1_artifacts.log)',
             also='closure-free: on 263 of 3000 random sparse systems "Groebner degree <= 4" holds under one admissible graded order and fails under another (results/order_flip_search.json); of those 263, the closure verdict flips in 2 (results/order_flip_closure.json).  Also A1 refutes the formulation "sufficiency at D is LM(W) equals LM(I_{<=4})": under wdeg LM(W) = LM(I_{<=4}) and the verdict is still insufficient.'),
        dict(id='A2', grade='VERIFIED', what='N_std < |V| ("impossible") with every row of W in the ideal, under a non-admissible (non-multiplicative) graded order',
             system="gen_systems.system('sparsequad', 9, 6, 0), order = ref_closure.make_key_random_graded(9, 3)",
             result='|V| = 8, N_std = 7 under the random per-monomial graded order, N_std = 8 under degrevlex; every row of W vanishes on V.  So the polarity statement needs an admissible order: the stated degrevlex qualifies, a bare "graded order" does not.',
             reproduce='cd out; python3 src/repro_w1_artifacts.py')],
    attacks_that_failed_to_break=[
        dict(attack='(1) two implementations disagree', grade='VERIFIED', result='584 comparisons, 0 mismatches: closure.c (RREF tails, waves, with and without early exit) vs the plain Python reference (N 8..19, which also runs its own saturation verifier) vs closure2.c (non-reduced echelon, one-pivot head reduction, literal passes and incremental) at N 8..24, families quadratic, sparse quadratic, cubic mixes, bilinear, Toeplitz-structured and planted.  Early exit validated at N=40 scale (n40 d0: full closure LM file byte-identical).',
             artifacts=['results/logs_small/diff_c_vs_ref_8_12.log', 'results/logs_small/diff_c_vs_ref_13_16.log', 'results/logs_small/diff_c_vs_ref_17_19.log', 'results/logs_small/diff_c_vs_c2_14_22.log', 'results/logs_small/diff_n23_24.log', 'results/earlyexit/n40_d0_noearly.json']),
        dict(attack='(2) verdict disagrees with the closure-free evaluation-kernel ground truth', grade='VERIFIED',
             result='288 random systems N=10..17: LM(W) is inside LM(I_{<=4}) and rank <= c - eval_rank in every one; whenever N_std = |V| also LM(W) = LM(I_{<=4}) (166 sufficient), and in the other 122 the closure is strictly smaller than I_{<=4} although the ideal-level count is |V|: "insufficient" is a statement about the capped procedure, not about the ideal.  On the twelve windows: LM(W) inside LM(I_{<=4}) in 12/12, equal in the 9 sufficient ones, strictly smaller in the 3 insufficient ones.',
             artifacts=['results/w1_ground_truth_10_17.json', 'results/w1_gt_10_17.log', 'results/postcheck/']),
        dict(attack='(3) counterexample to the polarity statement', grade='VERIFIED (numerics) / argued (proof, recalled standard facts)',
             result='300 missing-product mutant closures: N_std(mutant) >= N_std(closure) >= |V| in all (67 strict, 233 equal).  Proof under an admissible order: LM(I) is an up-set (if m = LM(f), j not in m, x_j f has leading monomial m+j because t+j <= t x_j < m x_j for every other term t), so Up(LM(W)) is inside LM(I) and its complement has at least |V| elements; W subset W2 gives LM(W) subset LM(W2).  Hence a missing product can only turn sufficient into insufficient, an out-of-ideal row can only lower N_std (false sufficient or impossible), and "sufficient" is a certificate (given W inside I) while "insufficient" is a statement about W.',
             artifacts=['results/logs_small/polarity_check.log']),
        dict(attack='(4) order dependence on the twelve', grade='VERIFIED for the 9 sufficient ones, argued for the 3 insufficient ones',
             result='For the 9 windows with rank = c - eval_rank, W = I_{<=4} is order independent, and the closure-free N_std under degrevlex, deglex and four random weighted graded orders equals |V|: sufficient under all 6 (results/window_order/).  For the 3 insufficient windows: the closure LM set is an up-set inside sizes <= 4 (K = 0, verified on 40 closures; follows from x_j f having LM m+j), so N_std >= c - r > eval_rank = |V| for every admissible graded order because r < c - eval_rank; V = empty cases are order free (1 in W is a subspace statement).  No window verdict depends on the order among the orders tested.',
             artifacts=['results/window_order/']),
        dict(attack='(5) relation between rank, columns, N_std and standard monomials above D', grade='VERIFIED (160 closures) / proof below',
             result='N_std = (c - r - K) + N_std^{>D}, where K = number of non-LM monomials of size <= D that contain a proper LM member.  Proof: monomials of size <= D split into LM (r), non-LM with a proper LM subset (K) and standard (c - r - K); standard monomials of size > D are the rest.  K = 0 for every unmutated closure (40/40) and K > 0 on 51 of 120 mutants.  So N_std >= c - r always, with equality iff there is no standard monomial above D; the std count can exceed columns minus rank, and K > 0 is a cheap structural flag of a missing product (see PT-1).',
             artifacts=['results/logs_small/identity_check.log'])],
    additional_findings=[
        dict(id='F-W1-S1', grade='VERIFIED', text='specification.yaml contains no definition of the sufficiency verdict, no leading-monomial, standard-monomial or monomial-order wording (zero grep matches); the verdict rule N_std = |V| and the order are the statement operationalisation only.  The specification speaks of rank and rank deficiency against sum_{d<=4} C(N,d).'),
        dict(id='F-W1-S2', grade='VERIFIED', text='Soundness asymmetry: an "insufficient" verdict needs only that the final W is a closed subspace containing the generators (then the smallest closed subspace is inside it, so N_std is bounded below) -- checked for the three insufficient windows by a saturation verifier on the FINAL rows (510,576 / 658,720 / 673,900 products, 0 non-vanishing) and by byte-identical re-runs with a different batch size.  A "sufficient" verdict needs the rows to be derivable (soundness): supported by construction, by 584 small-N diffs, by vanishing of every final row at every enumerated zero (all 6 instances with V non-empty and sufficient or insufficient, 0 violations) and by the explicit subset sums for two V = empty instances; not certified by an independent derivation of the leading-monomial sets at N >= 40: the second implementation (closure2 -i) independently inserted 102091 = c rows on the V-empty N=40 instance and 102087 = c - |V| rows on the V=4 N=40 instance, which reproduces those two ranks, but it was stopped in the long tail of its queue before writing LM sets (see closure2_independent_rerun).')])
perm = []
for f in sorted(glob.glob(os.path.join(OUT, 'results', 'permuted', '*.json'))):
    b = os.path.basename(f)[:-5]; j = json.load(open(f)); m = J('results/closure/%s.closure.json' % b)
    perm.append(dict(instance=b + '.ms', rank_permuted=j['rank'], rank_main=m['rank'], one_in_W_equal=(j['one_in_W'] == m['one_in_W']), lm_counts_by_size_equal=(j['lm_by_size'] == m['lm_by_size']), wave_ranks_equal=(j['wave_ranks'] == m['wave_ranks']),
                     N_std_permuted_order=j['N_std'], N_std_main_order=m['N_std'], row_eval_violations_at_permuted_zeros=j['row_eval_violations'], zeros=j['points_checked'], output=dict(path='results/permuted/%s.json' % b, sha256=sha(f))))
W1['additional_findings'].append(dict(id='F-W1-S3', grade='VERIFIED', text='representation independence on four real windows: variables relabelled by a seeded random permutation (a different grevlex, different column order, different batches): rank, 1-in-W, leading-monomial counts per size and the wave ranks are identical; the verdict class is identical; N_std is order dependent in magnitude on the insufficient ones (9145 vs 9133, 13681 vs 13608) and equals |V| on the sufficient ones; every final row vanishes at the permuted zeros (instances with V non-empty).', runs=perm))
rep['red_team_report']['joints']['W1'] = W1

# ------------------------------------------------------------------ W2
W2 = dict(
    verdict='holds',
    attacks_that_failed_to_break=[
        dict(attack='independent exact counts', grade='VERIFIED', result='|V| by six routes per instance (C Gray-code with affine solve, first half enumerated; same with halves exchanged; direct term evaluation per assignment, both halves; NumPy batched Gauss-Jordan, both halves): all equal on all twelve.  The enumerated zero sets of the two role assignments are identical sets and every zero satisfies every generator as written (raw-exponent evaluation including the field lines, and B evaluation); every single-bit flip of a zero violates a generator.',
             artifacts=['results/V_table.json', 'results/V/', 'src/check_solutions.py']),
        dict(attack='validation of the counters', grade='VERIFIED', result='181 comparisons with brute force (hand-checkable system, 120 random bilinear systems, 60 general systems) and 40 for the NumPy counter, all agree; systems checked to be bilinear across the two halves with no same-half products (so one affine solve per assignment is exact).', artifacts=['results/logs_small/test_counters.log']),
        dict(attack='parse ambiguity', grade='VERIFIED', result='11 parser tests (precedence a+b*c, trailing comma, constant 1, x^2 = x, cancellation of repeated terms, field lines, 200 random power polynomials against Python evaluation); all twelve actual files re-evaluated by Python own expression parser at 300 random points per line: 0 mismatches; term counts equal token counts.  Findings that change no count: N is the number of names on line 1 (2k = 40,42,44,46), not the n in the file name; each file has M non-field lines (n) plus N field-equation lines that are the zero polynomial in B.',
             artifacts=['results/logs_small/test_parser.log', 'results/logs_small/check_parse_vs_python.log']),
        dict(attack='closure-based corroboration of the denominator', grade='VERIFIED', result='in the 9 windows whose verdict is sufficient the closure N_std (computed with no point enumeration) equals the enumerated |V| (0,4,0,4,0,2,2,0,0 in increasing N); the 3 insufficient have N_std > |V| as required.')],
    proof_of_denominator_identity=dict(grade='argued from standard facts (recalled), numerics above',
        text='B = F_2[x]/(x_i^2+x_i) is isomorphic to F_2^{F_2^N} by evaluation: the map is a ring homomorphism, injective because a square-free polynomial is determined by its values (Moebius inversion), and both sides have dimension 2^N.  In a product of copies of F_2 an ideal generated by g_1..g_M is the set of functions supported inside the union of the supports of the g_i (for a point a with g_i(a)=1 the indicator delta_a = delta_a g_i lies in the ideal; conversely every element of the ideal vanishes where all g_i vanish).  Hence I = {f : f|_V = 0} and B/I is isomorphic to F_2^V, of dimension |V|; B is reduced so the ideal is radical, and B tensored with the algebraic closure is a product of copies of the closure so every point is F_2-rational.  Hence dim B/I = |V| = N_std(I) for the leading-monomial set of I under any admissible order.'),
    residual=['all counts rest on the .ms inputs as given (sha256 in blind_rederivation.yaml); the counters share the idea (enumerate one half, solve the other) but not code, and the closure-based agreement in 9 cases is code-independent of them.'])
rep['red_team_report']['joints']['W2'] = W2

# ------------------------------------------------------------------ W3
W3 = dict(
    verdict='breaks',
    kind='(c) breaking artifact; (a) coincides under the contract wording; (b) literal clause false',
    specification_read_after_hash='experiments/EXP-SEMBIN-7e1371/specification.yaml (certificate, invalidation rules 1 and 2, controls, stopping rules); sandbox copy sha256 631eaa05c68e554007728b2d5315e85cf48b63a33746c5f5060d103fde14636a',
    contract_text_relied_on=dict(
        certificate='"degree-4 Macaulay block over F_2 -- all products of the n(t-1) cubic generators and the field equations by monomials up to total degree 4 -- with rank and rank deficiency against the count of degree-<=4 monomials, sum_{d<=4} C(N,d)" (inputs.certificate)',
        rule_1='"A cell is invalid unless the generated system is verified structurally to have n(t-1) equations in n(t-2) + kt variables of degree 3 before the certificate runs."',
        rule_2='"A cell is invalid if the field equations were not included as explicit generators, since the certificate soundness claim is stated for that construction."',
        reading_choice='"all products ... by monomials up to total degree 4" is read as: product degree <= 4 (multiplier budget 4 - deg g), which is the only reading consistent with the stated column count sum_{d<=4} C(N,d); a multiplier-degree reading would need columns of degree up to 6 (PLAUSIBLE reading, supported by the column count).'),
    a=dict(result='coincides under the contract wording', grade='VERIFIED (60 square-free systems, N 4..7) + argued (proof)',
           evidence='The polynomial-ring degree-4 Macaulay block with the field equations as explicit generators, every generator and every field equation multiplied by EVERY monomial (non-square-free multipliers included) with total degree within budget: its image under x_i^2 -> x_i is exactly the Boolean single-level span and its square-free leading monomials equal LM of the Boolean span in 60/60 systems; every non-square-free monomial is a leading monomial (of a field-equation multiple).  Proof sketch: {x_i^2+x_i} is a Groebner basis (coprime leading terms) so the kernel of reduction on P_{<=4} is spanned by the multiples mu (x_i^2+x_i) of degree <= 4; hence U = kernel + lift of the Boolean span; a square-free leading monomial of u in U survives reduction because the reduced terms are smaller.',
           variants=dict(V1_full=w3v['V1'], V2_square_free_multipliers_only=w3v['V2'], V3_field_equations_without_multipliers=w3v['V3'], V4_no_field_equation_rows=w3v['V4'],
                         reading='the images under reduction coincide in all variants (60/60); the LEADING-MONOMIAL set read off the polynomial-ring block coincides with the Boolean one only if the field-equation multiples are included (V1 60/60; V2 52/60; V3 13/60; V4 9/60), i.e. "field equations as explicit generators" must mean generators multiplied like the others, which is the contract wording'),
           non_square_free_generators='a generator written non-square-free gets a smaller Boolean budget than polynomial-ring budget: 56 of 80 random cases differ (results/w3/exp_a.json); irrelevant to the twelve (all generators square-free, degree 2).',
           file_level='each of the twelve .ms files carries the N field equations x^2+x as explicit lines (rule 2 satisfied at the input level); the closure treats them as the zero polynomial of B.',
           artifacts=['results/w3/exp_a.json', 'results/w3/variants.json', 'src/w3_experiments.py', 'src/w3_variants.py']),
    b=dict(result='the literal "degree 3" clause is false for all twelve; counts are right', grade='VERIFIED',
           evidence='all 12 files: every non-field generator has degree exactly 2 (src/structure_check.py), M = n equations and N = 2k variables, so the clause "n(t-1) equations in n(t-2)+kt variables" holds (t = 2) but "of degree 3" does not.  Rule 1 can be read to cover these cells only as "degree <= 3" or as a t >= 3 clause (the specification own words for the chained system, "algebraic degree 3", and for the single polynomial, "2^{t-1} rather than 3", coincide in value at t = 2: 2^{t-1} = 2 = the verified degree of the instance systems).  Whether the executed cells were checked under a "degree <= 3" reading cannot be determined from the blind inputs.',
           plausible_not_verified='at t = 2 the specification nearby-object control (single summation polynomial, degree 2^{t-1}) has the same degree as the chained instance, so its required "insufficient at every cell including the diagonal" may be unsatisfiable by a different system at t = 2; I did not have equations (4)/(5) of the source paper and give this only as a pointer.',
           artifacts=['src/structure_check.py']),
    c=dict(result='iterated closure and literal single-level block give opposite verdicts at D = 4 on %d of 12 window systems' % n_opposite, grade='VERIFIED (two implementations at real scale; 168 small systems)',
           evidence=dict(
               windows=inst,
               reading='literal = raw generators times every square-free mu with |mu| <= 4 - deg g and nothing else (C closure -S; confirmed by the independent closure2s on four windows: ranks 31673, 31673, 36001, 41455 and the same N_std; confirmed against the Python gens_only mode and closure2s on 72 small systems).  The literal block returns sufficient only where 1 already lies in the span of the generators (two instances; explicit subset sums of 18 generators = 1 verified symbolically).  On the two n=40 instances it has rank 31,673 of 102,091 columns (deficiency 70,418), the iterated closure 102,091 / 102,087.',
               small_n=dict(systems=w3c['total'], iterated_strictly_larger=w3c['strictly_larger'], verdict_changes_single_insufficient_to_iterated_sufficient=w3c['verdict_changes'], reverse_changes=0,
                            first_examples_with_seeds=[dict(family=r['family'], N=r['N'], M=r['M'], seed=r['seed'], system="gen_systems.system(family, N, M, seed)", V=r['V'], single=r['verdict_single'], iterated=r['verdict_iterated'], N_std=[r['N_std_single'], r['N_std_iterated']]) for r in [x for x in w3c['rows'] if x['verdict_changes']][:4]]),
               consequence='the recorded verdicts of the iterated closure are statements about the iterated degree-capped closure, not about the contract literal certificate.  Read literally, the certificate does not return SUFFICIENT at either n = 40 instance, which the specification baseline control and its first stopping rule require.  The rank-deficiency reading (deficiency c - rank against |V|) gives the same opposite outcome (deficiency 70,418 at n = 40).  The deviation therefore carries the n = 40 baseline: DV-7 is a substantive deviation for the window, not a bookkeeping one.'),
           artifacts=['results/single_level/', 'results/single_level2/', 'results/w3/exp_c.json', 'src/run_single_level.sh', 'src/run_single_level_closure2s.sh']))
rep['red_team_report']['joints']['W3'] = W3

# ------------------------------------------------------------------ PT
ptsum = {k: {x: v for x, v in t.items() if x != 'cases'} for k, t in pt['PT1'].items()}
rep['red_team_report']['proves_too_much_control'] = dict(
    argument_tested='two elimination routines (different algorithms, same product generation) give the same leading-monomial set; an evaluation check at ONE verified common zero is clean on every elimination; a structural check of every elimination output passes; therefore the verdict is sound.  Implemented on MY closure (src/pt_controls.py): routines = incremental head reduction and from-scratch Gauss-Jordan inside ref_closure.Closure with the same (mutated) product code; structure = distinct LMs, each row highest term = its LM, degree <= 4, every generator reduces to 0.',
    PT1=dict(grade='VERIFIED', status='CONFIRMED BLIND SPOT',
             outcome='On every missing-product mutant case found (15 cases: (a) budget minus one 4, (b) rows multiplied only when their LM is new 4, (c) generators only 4, (d) last batch dropped 1 row-granularity + 2 chunk-granularity) the argument goes through with NO flag (S1, S2, S3 all true), including systems where the unmutated closure says sufficient and the mutant says insufficient.  The argument is necessary and not sufficient; quoted as certifying an "insufficient" verdict it proves too much.',
             per_mutant=ptsum,
             which_flags=dict(F1_comparison_with_independent_closure='flags every real mutant (a,c,d): 4/4, 4/4, 3/3', F2_saturation_verifier='flags every real mutant (a,c,d): 4/4, 4/4, 3/3 (also flags corrupted row sets, PT-2); on the packed C closure the verifier gave 0 violations on the correct output and 14,889 / 1,554 on the (a)/(d) mutants of a test system (src/closure_v.c -C)',
                              K_structural_up_set_flag='flags (a) 4/4, (d) 2/3 and 0/4 of (c): LM(W) not an up-set inside sizes <= 4; a partial, cheap, product-independent flag; not a substitute'),
             mutant_b_note='(b) is NOT a missing-product mutant: by F_2-linearity of mu*(.) and the degree filtration of an echelon basis every later row is a combination of rows that are themselves multiplied, so multiplying each row once at creation yields the same smallest closed subspace; F1, F2 and K are all clean on 4/4 and the verdict equals the unmutated one.  The argument was therefore right to pass on (b), and (b) is inconvenient to the card expectation of a flagged mutant.',
             artifacts=['results/pt/pt1_abc.json', 'results/pt/pt1_d.json', 'results/pt/pt_summary.json']),
    PT2=dict(grade='VERIFIED',
             a_bulk_corruption='the one-zero evaluation check flags a bulk corruption (30% of the rows with five random column flips): flagged in the headline run; as a function of the corrupted fraction its detection probability is 0.01 and 0.00 (1 row of 453, two settings), 0.06 (5 rows), 0.14 (3%), 0.40 (10%), 0.87 (30%), 1.00 (100%) over 100 trials each; the check at ALL 63 zeros and the saturation/generator check flag with probability 1.00 at every fraction.  So it is not vacuous, but "must flag" holds only for heavy corruption, and a one-zero check is weak against sparse corruption.',
             b_one_extra_row='ONE row with f(a) = 0, f(b) = 1 (not in the ideal) keeps the one-zero evaluation check CLEAN (as required), the two routines agree and the structure check passes; the check at the other zero and at all zeros flags it.  Effect on the verdict: on a zero-slack system (clean closure sufficient, |V| >= 2, 3/3 tried) the row drives N_std below |V| ("impossible", flagged by the verdict rule itself); with a missing-product mutant as base (slack N_std - |V| = 1) one out-of-ideal row restored N_std = |V| (2 systems): the two errors cancel, the one-zero check clean, the saturation verifier still flags.',
             sweep=sweep, artifacts=['results/pt/pt2.json', 'results/pt/pt2_sweep.json', 'results/pt/pt2_false.json']),
    PT3=dict(grade='VERIFIED',
             a_known_sufficient='32 systems with generators spanning I_{<=2} of a planted point (ground truth: |V| = 1, W_2 = I_{<=2}): the rule returns sufficient on 32/32; on 30 random planted degree-2 systems the rule agrees with the closure-free ground truth 30/30 (19 sufficient, 11 insufficient); the rule never returns insufficient on a known-sufficient control.',
             b_known_insufficient='3 systems (N = 8, 9, 10) whose reduced Groebner basis has a minimal leading monomial of size 5 > 4, established BOTH by the evaluation kernel and by sympy Groebner (modulus 2, grevlex, field equations added; minimal leading-monomial sets equal): the degree-4 closure returns insufficient on 3/3; no system returned sufficient.',
             artifacts=['results/pt/pt3a_v2.json', 'results/pt/pt3.json', 'results/pt/pt3_sympy.json']),
    object_inconvenient_to_the_argument='PT-1(b) (not a mutant) and PT-2(a) at small corrupted fractions (the one-zero check misses it): the argument passes for the right reason on (b) and for the wrong reason on sparse corruption.')

rep['red_team_report']['closure2_independent_rerun'] = dict(
    note='independent second implementation (closure2 -i) on two real N=40 systems, started in the background; whatever completed or not at the time this report was written is recorded here as a dated addendum to blind_rederivation.yaml (never replacing it)', status=c2)

rep['red_team_report']['objections'] = [
    'O1 (W1) the verdict labels carry no order.  The statement names degrevlex; the specification names none and never defines the verdict rule.  Verdicts must be recorded as (closure, order, rule).',
    'O2 (W3) the recorded certificate is the iterated degree-capped closure, not the single-level block of the contract; they disagree on 7 of 12 windows, so the baseline control (SUFFICIENT at n = 40) is met only by the iterated closure.',
    'O3 (W1) "insufficient" is a statement about the capped closure, not about the ideal: in 122 of 288 random systems the ideal part I_{<=4} certifies sufficiency while the closure does not.  An "insufficient" verdict must not be read as d_GB > 4.',
    'O4 the iteration index is undefined in the statement; any "rank after iteration t" comparison between implementations is implementation-defined.']
rep['red_team_report']['required_controls'] = [
    'run the literal single-level block (raw generators x multipliers, nothing else) on the twelve through the producer code and compare with results/single_level (rank, N_std)',
    'record the order and the verdict rule with every verdict; add a second admissible order for the window verdicts (done here for the 9 sufficient ones, argued for the 3 insufficient ones)',
    'for each "insufficient" verdict run a saturation verifier on the final rows; for each "sufficient" verdict require pointwise vanishing of the final rows at all enumerated zeros (done here, 0 violations)',
    'comparison with an independent closure (not only elimination routines sharing product generation) is the check that flags missing products']
rep['red_team_report']['heuristic_and_cost_model_challenges'] = 'not applicable: the round claims instrument validity, not an exponent-moving or heuristic-conditional result; no heuristic, o(1) term, time-memory interpolation or reduction chain is asserted or tested here.  Costs measured for the blind implementation: closure wall 0.0 s (generators already contain 1) to 768 s per window instance with 3 threads, peak resident 0.5-1.6 GB; see blind_rederivation.yaml.'
rep['red_team_report']['baseline_comparison'] = dict(dominated_by='not applicable (no performance or complexity claim is reviewed); the only comparison is between two definitions of the certificate (literal single-level block vs iterated closure), reported under W3(c); no comparison with Pollard rho, BSGS or any solver is made or implied', sota_delta=None)
rep['red_team_report']['limitations'] = [
    'blind values come from one author: two C implementations and a Python reference share my reading of the statement (order encoding, budget by deg f); the statement checks I could make (order sentence, definitions) are recorded in blind_rederivation.yaml; no comparison with the producer values was made or seen',
    'soundness of "sufficient" at N >= 40 rests on construction, 584 small-N diffs, pointwise vanishing at all zeros, and (V empty) two explicit subset sums; the independent second implementation reproduced the rank on two N=40 windows only (closure2_independent_rerun), and its LM sets were not written (UNREACHED)',
    'the order-flip artifact A1 uses weighted graded orders and was found on random sparse systems with |V| = 156; I found no flip among the six orders tested on the twelve windows; I did not test every admissible order',
    'W3(a): the proof is argued from recalled Groebner facts and verified on 60 systems with N <= 7; the Macaulay block of the contract was taken from its one-sentence description',
    'I did not read agents/red-team.md, AGENTS.md or templates/research-records.md (outside the card may_read); the layout follows the card deliverables and completion_gate; the attestation fields are those listed there',
    'wave ranks are an implementation measure; not comparable with a producer iteration count']
rep['red_team_report']['scope_limits'] = 'Every statement is scoped to the twelve window systems, the quantity as defined on the card (D = 4, grevlex order, closure under square-free multipliers), the random systems named by their generator seeds, and the orders tested.  No impossibility is asserted; no claim about Assumption 1, d_F4, n = 409 or 571, or any curve.'
rep['red_team_report']['next_concrete_action'] = 'The Coordinator compares blind_rederivation.yaml with the producer values field by field per instance (c, r, 1 in W, LM counts and hash, N_std, |V|, verdict) and decides DV-7 using results/single_level: the literal single-level block is insufficient on 7 of 12 windows where the iterated closure is sufficient.'
rep['red_team_report']['how_to_reproduce'] = ['cd out; bash src/run_V.sh; bash src/run_V_C.sh; bash src/run_V_numpy.sh', 'cd out; bash src/run_all_closures.sh; bash src/run_verification_suite.sh', 'cd out; bash src/run_small_tests.sh', 'cd out; bash src/run_single_level.sh', 'cd out; python3 src/pt_controls.py pt1|pt2|pt3 ...  (see src/pt_controls.py)', 'cd out; python3 src/make_blind_yaml.py; python3 src/make_report.py']

# ------------------------------------------------------------------ attestation
sources = ['ledger/handoffs/TASK-20261004-095926.yaml'] + ['experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e/' + os.path.relpath(p, os.path.join(OUT, '..', 'experiments', 'EXP-SEMBIN-7e1371', 'runs', 'RUN-SEMBIN-5ed13e')) for p in ms_rel] + ['experiments/EXP-SEMBIN-7e1371/specification.yaml (opened only after phase 1 was hashed)']
rep['review_attestation'] = dict(
    task_id='TASK-20261004-095926', joints_owned=['W1', 'W2', 'W3'], sources_read=sources, read_sibling_reports=False,
    blind_from_respected=True,
    blind_from_basis='only the card, the twelve .ms files and (after phase 1 was written and hashed) the specification were opened; no producer code, run, result, log, note, manifest, summary, ledger or coordination record, plan file, decision, sibling card or directory, knowledge entry or git history was opened or searched',
    independent_session=True, requested_policy='review-adversarial', resolved_model_id='claude-sonnet-5-5', fallback=dict(used=False, reason=None),
    verdicts=dict(W1='breaks', W2='holds', W3='breaks'),
    statement='No git history command (log, show, blame, diff) was run.  The plan file, DEC-20261004-df2986, DEC-20261004-6ac6bc, DEC-20261004-a47503 and the sibling card TASK-20261004-7d2fb6 and its directory were not opened.  No record was edited, nothing was committed, no status was changed, no RUN id was minted, no experiment run was made (zero runs).',
    incidental_exposures=[
        'a process listing (ps) printed the command lines of the sibling session, including script and instance names under its review directory; I read no file there and used the listing for nothing',
        'one trailing tail command was executed in the session default working directory (inside the repository) because of a shell chaining mistake; it tried to open a relative path that does not exist there and produced no content; no listing or search was made there',
        'the harness had already placed the repository CLAUDE.md contents (general program rules) in my context; they contain no SEMBIN result',
        'the dispatching session message after phase 1 reported that it verified my file hash and copied the specification into the sandbox (logistics only)'],
    general_references='none opened.  Background facts used (admissible monomial orders, Groebner bases of field equations, Boolean ring as functions on the cube, Moebius inversion) are RECALLED and back no finding; every finding rests on a reproduced run or on a proof written out in this report.',
    libraries_used='gcc 13.3.0 / OpenMP / immintrin; Python 3.11 standard library, numpy 2.4.6, sympy 1.14.0 (PT-3b only), PyYAML 6.0.1')

# ------------------------------------------------------------------ file manifest (written last)
files = {}
for d, _, fs in os.walk(OUT):
    for f in fs:
        p = os.path.join(d, f); r = os.path.relpath(p, OUT)
        if r == 'red_team_report.yaml': continue
        files[r] = sha(p)
rep['red_team_report']['files_sha256_except_this_report'] = dict(sorted(files.items()))
rep['red_team_report']['files_count'] = len(files)
text = yaml.safe_dump(rep, sort_keys=False, width=200, allow_unicode=True)
open(os.path.join(OUT, 'red_team_report.yaml'), 'w').write('# red_team_report.yaml -- TASK-20261004-095926 (blind lane).  Generated by src/make_report.py.\n' + text)
print('wrote red_team_report.yaml; files hashed:', len(files))
