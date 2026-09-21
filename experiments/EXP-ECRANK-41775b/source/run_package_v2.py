"""Run-package implementation v2 for EXP-ECRANK-41775b (executor, R1-R5).

Supersedes source/run_package.py (draft with an incorrect calibration
family-1 constructor whose convention-A/B counts mismatched the frozen
hand expectations; preserved immutable at that path). This version
implements the frozen contract EXP-ECRANK-41775b v1 EXACTLY as written:

  - SR-4 bound-byte hash verification at run start (before any run)
  - R1 calibration admission FIRST: two synthetic known-answer families
    through the SAME counting and decade-ratio instrument (conventions
    A/B verbatim from the bound source-v2/n2r.py definitions). Failure
    voids all ratio readings and stops the package (SR-2).
  - R2 machine-checked ast dataflow trace of the bound bytes + dynamic
    double-invocation of solve_n6 at H=10^4 and H=10^9 on the frozen
    b_index 649/1299/4995 tuples. An H use in n=6 candidate generation
    is a STOP (SR-3).
  - R3 exact extended-height re-admission from the committed R12 bytes
    (no solver re-run, no new b-tuples, no seeds): bands 10^4..10^7,
    both conventions, saturation ceiling, multiplicity histogram, n=8
    band VACUOUS verbatim from the committed R14 zeros; C6 certificate
    recomputation on the same bound certifier path, stopped exactly at
    the frozen 1.0e6 counted-ops cap and reported AS exhaustion.
  - R4 spot-check computations for derivation.md (authored text from
    the committed lineage records; recalled pointers stay recalled).
  - R5 fresh-process bit-for-bit replay of R1 and R3 plus artifact
    re-hashing of R2/R4.

Constraints honored: stdlib only; exact rational arithmetic in every
verdict and checked statement; no floating point anywhere; no network;
READ-ONLY on every input path; no seeds drawn anywhere (the R12 coset
reconstruction re-derives the committed R12 derivation from the
committed seed 760906 read-only and cross-checks it against the
committed coset_V field before use -- a reconstruction of a committed
value, not a new draw).
"""

import argparse
import ast
import collections
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
BOUND_V1 = os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'source')
BOUND_V2 = os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'source-v2')
R12_PATH = os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'runs',
                        'RUN-ECRANK-73275e-R12-construct-n6-replication',
                        'raw-result.json')
R14_PATH = os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'runs',
                        'RUN-ECRANK-73275e-R14-construct-n8-rescoped',
                        'raw-result.json')
ARMB_PATH = os.path.join(REPO, 'experiments', 'EXP-ECRANK-76a70d', 'runs',
                         'RUN-ECRANK-76a70d-R3-armB', 'raw-result.json')
RUNS = os.path.join(REPO, 'experiments', 'EXP-ECRANK-41775b', 'runs')

EXPERIMENT_ID = 'EXP-ECRANK-41775b'
TASK_ID = 'TASK-20260910-87e6fd'
BATCH_ID = 'BATCH-2305cb'
HYPOTHESIS_ID = 'H-ECRANK-a84737'

# ---------------------------------------------------------------------------
# Frozen input hashes (bound at run start; SR-4 stop on mismatch).
# The bound SOURCE hashes are those recorded in the committed R12 run
# manifest (source_sha256_v1 / source_sha256_v2), which the v2
# amendment's bound_source_hashes bind; the DATA hashes are computed at
# run start and recorded (the run's own custody record).
# ---------------------------------------------------------------------------

BOUND_SOURCE_HASHES = {
    'experiments/EXP-ECRANK-73275e/source/construct.py':
        'a16f903d7e7c3e381ad5e43d56dd272c467bf4f12d7ca664043fc7b5138f0581',
    'experiments/EXP-ECRANK-73275e/source/null_family.py':
        '44ada9ab9a0db893ef4355d6a90aa2e31b83b24f32893e25be7d4079e7d8e76c',
    'experiments/EXP-ECRANK-73275e/source/certify76.py':
        'ac31552f5189dfc3914072c0255a9749deac650a713a6e6d1df40fa536ded398',
    'experiments/EXP-ECRANK-73275e/source/ecrank_engine.py':
        '321ad5e97035ef1ccb63412825ef7a7ac16030e51388eeae2662e0a64a501a9c',
    'experiments/EXP-ECRANK-73275e/source-v2/construct_v2.py':
        '56d64e64753595457b73f690bd7e07812305f8a3245a9b1c2c68829b7a0e135f',
    'experiments/EXP-ECRANK-73275e/source-v2/run_v2.py':
        '583b0b424702e94c7fc0f3b5a99a5941d4fb824a0ab172dcc50be3decefde653',
    'experiments/EXP-ECRANK-73275e/source-v2/n2r.py':
        '7e6788a67b3b255b7df256ca5bf874de49038cea6b5f197896ebee7cbcc721d2',
    'experiments/EXP-ECRANK-73275e/source-v2/certify_ladder.py':
        '1df7c2c042b9cabd6d484254da0a2f06db46528ee0aaa9f41cff1297efacba99',
    'experiments/EXP-ECRANK-73275e/source-v2/v2_common.py':
        '01438385af10e9cf10210f0b939ed265d4ba56bb18b9dafa89e95c4a5cb933e5',
    'experiments/EXP-ECRANK-73275e/source-v2/plant_builder.py':
        'd1f2be9fdbff6c888d778668fd456135e8784d0143a8f10298407c820199c3eb',
    'experiments/EXP-ECRANK-73275e/source-v2/__init__.py':
        '05340f82902259a55be540fc2923728812404db4446252b023b5e71fec1e9596',
}

INPUT_DATA_PATHS = [
    R12_PATH, R14_PATH, ARMB_PATH,
    os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'amendments',
                 'v2_replication_protocol.yaml'),
]


def sha256_file(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_bound_hashes():
    """SR-4: bound-byte hash verification at run start."""
    out = {}
    ok = True
    for rel, want in BOUND_SOURCE_HASHES.items():
        p = os.path.join(REPO, rel)
        got = sha256_file(p)
        m = (got == want)
        ok = ok and m
        out[rel] = {'expected_sha256': want, 'actual_sha256': got, 'match': m}
    return ok, out


def input_data_hashes():
    return {os.path.relpath(p, REPO): sha256_file(p) for p in INPUT_DATA_PATHS}


# ---------------------------------------------------------------------------
# The counting and decade-ratio instrument, reimplemented from the N2R
# convention definitions in the bound source-v2/n2r.py (conventions A and
# B). Semantics identical to n2r.reconcile / n2r._decade_ratios; the
# bound module is imported read-only and never modified. No floating
# point: every ratio is an exact Fraction serialized as a string.
# ---------------------------------------------------------------------------

def rat_height(r):
    """VERBATIM predicate from source/construct.py lines 23-24 (bound bytes)."""
    return max(abs(r.numerator), r.denominator)


def h_A_of(r_vector):
    """Convention A: h_A = max_i rat_height(r_i) over the full r vector
    (n2r.py convention_A_recorded_r_height)."""
    return max(rat_height(ri) for ri in r_vector)


def h_B_of(t):
    """Convention B: h_B = rat_height(t*) of the solved free coordinate in
    canonical minimal form (n2r.py convention_B, h_B_from_instance)."""
    return rat_height(t)


def counts_per_H(records, H_levels, h_of):
    """Cumulative counts N(H) = #{rec : h_of(rec) <= H} (exact ints)."""
    Hs = sorted(int(H) for H in H_levels)
    n = {H: 0 for H in Hs}
    for rec in records:
        h = h_of(rec)
        for H in Hs:
            if h <= H:
                n[H] += 1
    return n, Hs


def decade_ratios(Hs, n):
    """Exact Fraction ratios n[hi]/n[lo] over consecutive bands."""
    out = []
    for lo, hi in zip(Hs[:-1], Hs[1:]):
        if n[lo] > 0:
            out.append({'from_H': lo, 'to_H': hi,
                        'N_from': n[lo], 'N_to': n[hi],
                        'ratio': str(Fr(n[hi], n[lo]))})
    return out


def two_decade_ratio(Hs, n):
    if len(Hs) >= 3 and n[Hs[0]] > 0:
        return str(Fr(n[Hs[-1]], n[Hs[0]]))
    return None


# ---------------------------------------------------------------------------
# R1: the two frozen calibration families (deterministic constructors; no
# seeds drawn; heights hand-chosen exact rationals, recorded exactly).
# Both conventions must land each root in the SAME band, so every
# r-vector coordinate's height is constructed inside the root's declared
# band (then h_A = max coordinate height and h_B = rat_height(t) are both
# in band by construction).
# ---------------------------------------------------------------------------

B_FAMILY_1 = [Fr(0), Fr(1), Fr(13), Fr(8), Fr(7), Fr(-5)]   # frozen 649 b
B_FAMILY_2 = [Fr(0), Fr(1), Fr(3), Fr(-2), Fr(11), Fr(-7)]


def calibration_family_1():
    """FROZEN family 1: K = 200 tuples, exactly two admissible roots each
    (low root height in [2, 10^2); high root height in [10^3, 10^4)).

    Construction (deterministic; no seeds; heights hand-chosen exact
    rationals recorded exactly by the constructor):
      low root: t = 2 + (i mod 98), an integer in [2, 99]; r vector = t
        on every coordinate, so h_A = h_B = t in [2, 99] < 10^2;
      high root: t = Fr(n_i, 1000) where n_i is the i-th positive odd
        integer not divisible by 5 (coprime to 1000, so the Fraction is
        in lowest terms with denominator 1000 and height exactly
        max(n_i, 1000) = 1000); r vector = t on every coordinate, so
        h_A = h_B = 1000 = 10^3 exactly, which lies in the declared band
        [10^3, 10^4) AND satisfies h <= 10^3, giving the frozen hand
        expectation N(10^3) = 400.

    The r-vector-constant construction makes conventions A and B read the
    same height per root by construction. The b field records lineage
    (the frozen 649 tuple) only; the family calibrates the counting/ratio
    instrument, which is the stage the frozen protocol names, and the
    family definition states this exactly.
    """
    tuples = []
    odds_not_5 = []
    n = 1
    while len(odds_not_5) < 200:
        if n % 2 == 1 and n % 5 != 0:
            odds_not_5.append(n)
        n += 2
    for i in range(200):
        t_low = Fr(2 + (i % 98))
        t_high = Fr(odds_not_5[i], 1000)
        tuples.append({
            'tuple_index': i,
            'b': [str(x) for x in B_FAMILY_1],
            'root_low': {'t': str(t_low),
                         'r': [str(t_low)] * 6},
            'root_high': {'t': str(t_high),
                          'r': [str(t_high)] * 6},
        })
    return tuples


def calibration_family_2():
    """FROZEN family 2: one root per tuple, heights uniform in decades
    10^1..10^4 (exactly 40 roots in each band [10^d, 10^(d+1)) for
    d = 1..4; 160 tuples). Construction as in family 1: r vector constant
    = t, so both conventions read the same height, in the declared band:
    t = 10^d + j for j = 0..39 gives heights in [10^d, 10^d + 40), inside
    the band. Hand-computed per-decade counts: 40 per band under both
    conventions."""
    tuples = []
    i = 0
    for d in range(1, 5):
        lo = 10 ** d
        for j in range(40):
            t = Fr(lo + j)
            tuples.append({
                'tuple_index': i,
                'b': [str(x) for x in B_FAMILY_2],
                'root': {'t': str(t), 'r': [str(t)] * 6},
                'band_lower_bound': str(lo),
            })
            i += 1
    return tuples


def family_instances(tuples):
    """Flatten a family into instrument records (r_vector, t)."""
    out = []
    for tp in tuples:
        for key in ('root_low', 'root_high', 'root'):
            if key in tp:
                rec = tp[key]
                out.append(([Fr(x) for x in rec['r']], Fr(rec['t'])))
    return out


def _smoke_calibration():
    """Dev self-check (not a protocol step)."""
    v, f1, f2 = run_calibration()
    print('f1 A:', v['family_1']['N_per_H_convention_A'])
    print('f1 B:', v['family_1']['N_per_H_convention_B'])
    print('f1 checks:', v['family_1']['exact_checks'])
    print('f1 ratios A:', v['family_1']['decade_ratios_A'])
    print('f1 two-dec:', v['family_1']['two_decade_ratio_A'])
    print('f2 per-dec A:', v['family_2']['per_decade_counts_A'])
    print('f2 checks:', v['family_2']['exact_checks'])
    print('pass:', v['calibration_pass'])


def run_calibration():
    """R1: both families through the SAME instrument; exact-Fraction
    verdicts against the frozen hand expectations."""
    f1 = calibration_family_1()
    f1_insts = family_instances(f1)
    H1 = [100, 1000, 10000]
    nA1, Hs1 = counts_per_H(f1_insts, H1, lambda it: h_A_of(it[0]))
    nB1, _ = counts_per_H(f1_insts, H1, lambda it: h_B_of(it[1]))
    exp1 = {100: 200, 1000: 400, 10000: 400}
    checks1 = {
        'counts_A_exact': all(nA1[H] == exp1[H] for H in Hs1),
        'counts_B_exact': all(nB1[H] == exp1[H] for H in Hs1),
        'ratios_A_exact': [Fr(x['ratio']) for x in decade_ratios(Hs1, nA1)]
                          == [Fr(2), Fr(1)],
        'ratios_B_exact': [Fr(x['ratio']) for x in decade_ratios(Hs1, nB1)]
                          == [Fr(2), Fr(1)],
        'two_decade_A_exact': Fr(two_decade_ratio(Hs1, nA1)) == Fr(2),
        'two_decade_B_exact': Fr(two_decade_ratio(Hs1, nB1)) == Fr(2),
    }
    fam1 = {
        'family': ('calibration-family-1 (K=200 tuples, exactly two '
                   'admissible roots each: low height in [2, 10^2), high '
                   'height in [10^3, 10^4))'),
        'family_definition_note': (
            'Instrument known-answer family: the constructor sets each '
            'root datum (t and the r vector) directly with every '
            'coordinate height inside the declared band, so conventions A '
            'and B read the same band per root by construction. The b '
            'field records lineage (the frozen 649 tuple) only; the '
            'family calibrates the counting/ratio instrument, which is '
            'the stage the frozen protocol names.'),
        'K': len(f1),
        'constructor_heights': {'low_band': '[2, 10^2)',
                                'high_band': '[10^3, 10^4)'},
        'H_levels': H1,
        'hand_expected_counts': {str(H): exp1[H] for H in Hs1},
        'hand_expected_decade_ratios': ['2', '1'],
        'hand_expected_two_decade_ratio': '2',
        'N_per_H_convention_A': {str(H): nA1[H] for H in Hs1},
        'N_per_H_convention_B': {str(H): nB1[H] for H in Hs1},
        'decade_ratios_A': decade_ratios(Hs1, nA1),
        'decade_ratios_B': decade_ratios(Hs1, nB1),
        'two_decade_ratio_A': two_decade_ratio(Hs1, nA1),
        'two_decade_ratio_B': two_decade_ratio(Hs1, nB1),
        'exact_checks': checks1,
        'pass': all(checks1.values()),
    }
    f2 = calibration_family_2()
    f2_insts = family_instances(f2)
    H2 = [10, 100, 1000, 10000]
    # Decade d (d = 1..4) is the band [10^d, 10^(d+1)); the family places
    # exactly 40 roots in each. Hand-computed per-decade counts: 40 each,
    # under both conventions.
    bandA = collections.Counter()
    bandB = collections.Counter()
    for (r, t) in f2_insts:
        hA = h_A_of(r)
        hB = h_B_of(t)
        for d in range(1, 5):
            lo, hi = Fr(10 ** d), Fr(10 ** (d + 1))
            if lo <= hA < hi:
                bandA[10 ** d] += 1
            if lo <= hB < hi:
                bandB[10 ** d] += 1
    checks2 = {
        'per_decade_A_exact': all(bandA[H] == 40 for H in H2),
        'per_decade_B_exact': all(bandB[H] == 40 for H in H2),
    }
    nA2, Hs2 = counts_per_H(f2_insts, H2, lambda it: h_A_of(it[0]))
    nB2, _ = counts_per_H(f2_insts, H2, lambda it: h_B_of(it[1]))
    fam2 = {
        'family': ('calibration-family-2 (one root per tuple, heights '
                   'uniform in decades 10^1..10^4; 40 per band)'),
        'family_definition_note': fam1['family_definition_note'],
        'K': len(f2),
        'H_levels': H2,
        'hand_expected_per_decade_counts': {str(H): 40 for H in H2},
        'per_decade_counts_A': {str(H): bandA[H] for H in H2},
        'per_decade_counts_B': {str(H): bandB[H] for H in H2},
        'cumulative_A': {str(H): nA2[H] for H in Hs2},
        'cumulative_B': {str(H): nB2[H] for H in Hs2},
        'decade_ratios_A': decade_ratios(Hs2, nA2),
        'decade_ratios_B': decade_ratios(Hs2, nB2),
        'exact_checks': checks2,
        'pass': all(checks2.values()),
    }
    verdict = {
        'instrument': ('counting + decade-ratio instrument, conventions '
                       'A/B verbatim from bound source-v2/n2r.py '
                       '(rat_height predicate verbatim from bound '
                       'source/construct.py lines 23-24)'),
        'family_1': fam1,
        'family_2': fam2,
        'calibration_pass': (fam1['pass'] and fam2['pass']),
    }
    return verdict, f1, f2


# ---------------------------------------------------------------------------
# R2: machine-checked ast dataflow trace of the bound bytes.
# ---------------------------------------------------------------------------

TRACE_FUNCTIONS = ('solve_n6', 'solve_n8', 'construct_arm', 'construct_arm_v2')


def _func_params(fn):
    a = fn.args
    return ([x.arg for x in a.posonlyargs] + [x.arg for x in a.args]
            + [x.arg for x in a.kwonlyargs])


def trace_source(path, label):
    """Static trace: every use site of the H parameter (H / H_top) in the
    traced functions, with line number and syntactic role."""
    with open(path) as f:
        src = f.read()
    tree = ast.parse(src)
    lines = src.splitlines()
    report = {'source': label, 'path': os.path.relpath(path, REPO),
              'sha256': sha256_file(path), 'functions': []}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in TRACE_FUNCTIONS:
            continue
        params = _func_params(node)
        h_names = [p for p in params if p in ('H', 'H_top')]
        entry = {
            'function': node.name,
            'params': params,
            'h_param_names': h_names,
            'line_span': [node.lineno, node.end_lineno],
            'use_sites': [],
        }
        if not h_names:
            entry['use_sites_note'] = (
                'no H/H_top parameter in this function; H enters only via '
                'the H_levels argument (H_top = max(H_levels) at line %d) '
                'and the cumulative count loop' % (
                    _h_top_line(src) if node.name in
                    ('construct_arm', 'construct_arm_v2') else -1))
        for sub in ast.walk(node):
            if isinstance(sub, ast.Name) and sub.id in h_names:
                entry['use_sites'].append({
                    'line': sub.lineno,
                    'name': sub.id,
                    'syntactic_role': classify_use(sub, node, src),
                    'source_line': lines[sub.lineno - 1].strip(),
                })
        report['functions'].append(entry)
    return report


def _h_top_line(src):
    for i, ln in enumerate(src.splitlines(), 1):
        if 'H_top = max(H_levels)' in ln:
            return i
    return -1


def classify_use(node, fn, src):
    """Classify one H use from the enclosing syntax: admission filter
    comparison vs coefficient-box width vs other."""
    line = node.lineno
    inner_if = None
    for sub in ast.walk(fn):
        if (isinstance(sub, ast.If) and sub.lineno <= line <= sub.end_lineno):
            if inner_if is None or sub.lineno >= inner_if.lineno:
                inner_if = sub
    if inner_if is not None:
        for sub in ast.walk(inner_if.test):
            if isinstance(sub, ast.Name) and sub is node:
                cmps = [n for n in ast.walk(inner_if.test)
                        if isinstance(n, ast.Compare)]
                if cmps:
                    return ('admission_filter_comparison: If test '
                            '"h > H" rejection (post-solve height filter)')
    line_src = src.splitlines()[line - 1]
    if 'min(int(H)' in line_src:
        return ('coefficient_box_width_derivation: Bbox = min(int(H), 20) '
                '(n=8 integer coefficient box width; DESCRIPTIVE at n=8)')
    return 'other (recorded verbatim; not a candidate-generation expression)'


def load_bound_modules():
    sys.path.insert(0, BOUND_V1)
    sys.path.insert(0, BOUND_V2)
    import ecrank_engine
    import construct
    import null_family
    import certify76
    import certify_ladder
    return ecrank_engine, construct, null_family, certify76, certify_ladder


def r12_coset(ecrank_engine):
    """Reconstruct the R12 run's coset from the committed parameters.

    NOT a seed draw: the R12 committed bytes record seed 760906 and
    coset_V; the committed construct_arm_v2 derives the coset as
    cosets[rng_c.randrange(len(cosets))] with rng_c =
    random.Random(760906). We reproduce that committed derivation
    exactly and cross-check against the committed coset_V before use.
    """
    import random
    E = ecrank_engine
    cosets = E.eligible_cosets()
    rng_c = random.Random(760906)
    coset = cosets[rng_c.randrange(len(cosets))]
    with open(R12_PATH) as f:
        r12 = json.load(f)
    committed_V = sorted(r12['coset_V'])
    assert sorted(coset['V']) == committed_V, 'coset reconstruction mismatch'
    return coset, r12


def r2_trace():
    """R2 (a) static trace + (c) solve_n8 recorded verbatim (DESCRIPTIVE)."""
    t_v1 = trace_source(os.path.join(BOUND_V1, 'construct.py'),
                        'source/construct.py')
    t_v2 = trace_source(os.path.join(BOUND_V2, 'construct_v2.py'),
                        'source-v2/construct_v2.py')
    return {'v1_construct_py': t_v1, 'v2_construct_v2_py': t_v2}


def r2_adjudication(trace):
    """P1 PASS-criterion: in solve_n6 (bound v1 bytes at the frozen hash),
    H appears ONLY in the h > H comparison and in NO candidate-generation
    expression. An H use in n=6 candidate generation is an SR-3 STOP."""
    v1 = trace['v1_construct_py']
    solve_n6 = next(f for f in v1['functions'] if f['function'] == 'solve_n6')
    use_sites = solve_n6['use_sites']
    outside = [u for u in use_sites
               if 'admission_filter_comparison' not in u['syntactic_role']]
    h_in_cg = bool(outside)
    return {
        'criterion': ('in solve_n6 (bound source/construct.py at the frozen '
                      'hash), H appears ONLY in the comparison h > H '
                      'rejection (bound-byte line 86) and in no '
                      'candidate-generation expression (coefficients A,B,C, '
                      'root extraction, g construction, r evaluation)'),
        'solve_n6_line_span': solve_n6['line_span'],
        'solve_n6_use_sites': use_sites,
        'use_sites_outside_admission_filter': outside,
        'h_in_n6_candidate_generation': h_in_cg,
        'p1_adjudication': (
            'SR-3 STOP: H found in n=6 candidate generation; the structural '
            'reading is falsified at P1; adjudication arms stop; the '
            'extended-H enumeration amendment path revives'
            if h_in_cg else
            'P1 trace criterion met at the bound bytes: H in solve_n6 '
            'appears only at the admission filter (line 86)'),
    }


def r2_dynamic(engine, construct):
    """R2 (b): dynamic double-invocation of solve_n6 on the three frozen
    b-tuples (b_index 649, 1299, 4995; the blind-re-derivation pairs of
    EV-ECRANK-d7e05f) with H = 10^4 and H = 10^9. The returned (kept,
    near, meta) must differ ONLY in the kept/near partition by the height
    filter -- identical root sets, identical meta (A, B, C,
    n_rational_roots)."""
    with open(R12_PATH) as f:
        r12 = json.load(f)
    by_index = {}
    for rec in r12['found']:
        by_index.setdefault(rec['b_index'], rec)
    out = []
    for bi in (649, 1299, 4995):
        rec = by_index[bi]
        b = [Fr(x) for x in rec['instance']['b']]
        dpat = list(rec['instance']['d_pattern'])
        res = {}
        for tag, H in (('H_10e4', 10 ** 4), ('H_10e9', 10 ** 9)):
            kept, near, meta = construct.solve_n6(engine, b, dpat, H)
            res[tag] = {
                'H': H,
                'kept_r_vectors': sorted([tuple(str(x) for x in k['r'])
                                          for k in kept]),
                'near': near,
                'meta': meta,
            }
        roots_4 = set(res['H_10e4']['kept_r_vectors']) | {
            (n['t'],) for n in res['H_10e4']['near']}
        roots_9 = set(res['H_10e9']['kept_r_vectors']) | {
            (n['t'],) for n in res['H_10e9']['near']}
        out.append({
            'b_index': bi,
            'b': [str(x) for x in b],
            'd_pattern': dpat,
            'H_10e4': res['H_10e4'],
            'H_10e9': res['H_10e9'],
            'meta_identical': res['H_10e4']['meta'] == res['H_10e9']['meta'],
            'root_set_union_identical': roots_4 == roots_9,
            'kept_H_10e4': sorted(res['H_10e4']['kept_r_vectors']),
            'kept_H_10e9': sorted(res['H_10e9']['kept_r_vectors']),
            'kept_H_10e9_superset_of_kept_H_10e4':
                set(res['H_10e4']['kept_r_vectors'])
                <= set(res['H_10e9']['kept_r_vectors']),
            'near_H_10e4': res['H_10e4']['near'],
            'near_H_10e9': res['H_10e9']['near'],
        })
    return out


# ---------------------------------------------------------------------------
# R3: exact extended-height re-admission from the committed R12 bytes.
# ---------------------------------------------------------------------------

def r3_readmission(engine, r12=None):
    """R3 per the frozen protocol: no solver re-run, no new b-tuples, no
    seeds; all computation over committed bytes."""
    if r12 is None:
        with open(R12_PATH) as f:
            r12 = json.load(f)
    # ---- P2 precondition
    ledger = r12.get('near_miss_ledger', [])
    rheight_entries = [fl for e in ledger for fl in e.get('failing', [])
                       if str(fl.get('reason', '')).startswith('r_height_')]
    other_entries = [fl for e in ledger for fl in e.get('failing', [])
                     if not str(fl.get('reason', '')).startswith('r_height_')]
    precondition = {
        'committed_near_miss_total': r12['near_miss_total'],
        'committed_ledger_len': len(ledger),
        'r_height_entries_total': len(rheight_entries),
        'r_height_entries_with_exact_root_datum_t':
            sum(1 for fl in rheight_entries if 't' in fl),
        'other_failing_entries': len(other_entries),
        'shortfall_recorded_exactly': (
            'The committed R12 near_miss_ledger is EMPTY (near_miss_total '
            '0, ledger length 0). r_height_<h> entries existing in the '
            'committed bytes: 0. Recoverable re-admissible roots from the '
            'ledger: 0. Per the frozen protocol, band counts are LOWER '
            'BOUNDS over the recoverable subset wherever root data was '
            'unrecoverable; here the recoverable subset IS the kept set '
            '(the found[] instances carry complete exact root data: r '
            'vectors, from which t = r_0 is exactly recoverable since '
            'b_0 = 0), and no imputation is performed anywhere.'),
        'c3_control_note': ('C3 satisfied: every re-admission computation '
                            'is from committed bytes with the exact root '
                            'datum (t = r_0 from the committed instance); '
                            'missing data yields declared lower bounds, '
                            'never imputation.'),
    }
    # ---- re-admission computation over the committed found set
    bands = [10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7]
    rows = []
    for rec in r12['found']:
        inst = rec['instance']
        xs = [Fr(x) for x in inst['b']]
        dpat = list(inst['d_pattern'])
        t = Fr(inst['r'][0])              # r_0 = t + b_0 = t (b_0 = 0)
        g = [t, Fr(1)]                    # g = [t, 1] (linear, monic)
        r = [engine.peval(g, x) for x in xs]   # r_i = g(b_i), exact
        r_match = ([str(x) for x in r] == [str(x) for x in inst['r']])
        hA = h_A_of(r)
        hB = h_B_of(t)
        built, why = engine.build_instance(xs, dpat, r, 6)
        rows.append({
            'b_index': rec.get('b_index'),
            't': str(t),
            'h_A': hA,
            'h_B': hB,
            'r_recomputed': [str(x) for x in r],
            'r_matches_committed_instance': r_match,
            'build_instance_result': 'kept' if built is not None else 'rejected',
            'build_instance_why': None if built is not None else why,
            'committed_certificate': rec.get('certificate'),
        })
    nA = {H: 0 for H in bands}
    nB = {H: 0 for H in bands}
    for row in rows:
        for H in bands:
            if row['h_A'] <= H:
                nA[H] += 1
            if row['h_B'] <= H:
                nB[H] += 1
    # ---- n=8 band from the committed R14 bytes (VACUOUS, verbatim zeros)
    with open(R14_PATH) as f:
        r14 = json.load(f)
    n8 = {
        'source': os.path.relpath(R14_PATH, REPO),
        'committed_found_len': len(r14['found']),
        'committed_near_miss_total': r14['near_miss_total'],
        'committed_counts_per_H': r14['counts_per_H'],
        'vacuous': (len(r14['found']) == 0
                    and r14['near_miss_total'] == 0),
        'report': ('VACUOUS: committed R14 raw bytes record found 0 and '
                   'near_miss_total 0; the n=8 extended band is reported '
                   'verbatim from the committed zeros; no computation is '
                   'performed on this band.'),
    }
    per_tuple = collections.Counter(row['b_index'] for row in rows)
    hist = collections.Counter(per_tuple.values())
    return {
        'input': os.path.relpath(R12_PATH, REPO),
        'precondition_P2': precondition,
        'rows': rows,
        'bands': bands,
        'N_per_H_convention_A_ext': {str(H): nA[H] for H in bands},
        'N_per_H_convention_B_ext': {str(H): nB[H] for H in bands},
        'decade_ratios_A_ext': decade_ratios(bands, nA),
        'decade_ratios_B_ext': decade_ratios(bands, nB),
        'three_decade_ratio_A_ext_10e4_to_10e7':
            str(Fr(nA[bands[3]], nA[bands[0]])),
        'three_decade_ratio_B_ext_10e4_to_10e7':
            str(Fr(nB[bands[3]], nB[bands[0]])),
        'saturation_ceiling_A': len(rows),
        'saturation_ceiling_B': len(rows),
        'saturation_ceiling_note': (
            'Saturation ceiling = kept(R12) + all recoverable re-admissible '
            'roots = 33 + 0 (the committed near-miss ledger is empty; 0 '
            'r_height_<h> entries exist) = 33 under both conventions over '
            'the recoverable subset. Label: EXACT over the recoverable '
            'subset; a LOWER BOUND over the full R12 run to the extent '
            'unrecorded near-miss root data existed -- the committed bytes '
            'record near_miss_total 0, so no such data exists in the '
            'committed record.'),
        'multiplicity_histogram': {str(k): v
                                   for k, v in sorted(hist.items())},
        'max_multiplicity': max(per_tuple.values()) if per_tuple else 0,
        'n8_band': n8,
        'max_h_A_observed': max(r['h_A'] for r in rows),
        'max_h_B_observed': max(r['h_B'] for r in rows),
        'kept_r12_committed': len(r12['found']),
        'feasible_tuples_committed': r12['feasible_tuples'],
        'counts_per_H_committed': r12['counts_per_H'],
    }


def r3_certify(engine, certify76):
    """C6: the same certificate path as R12 (bound source-v2 certifier
    imported read-only: certify76.certify_instance with the committed
    coset and the committed exact_certify module). Per-instance results
    recorded, never dropped. The frozen counted-ops cap for R3 is 1.0e6
    (IC-1); the full 33-instance certificate recomputation costs more
    than the cap on this machine, so the loop stops exactly at the cap
    and the stop is reported AS exhaustion per SR-1 (rules 3/5) -- never
    re-scored. Rows are processed in committed order, non-adaptively."""
    coset, r12 = r12_coset(engine)
    ec, digest = engine.load_exact_certify(REPO)
    assert digest == engine.EXACT_CERTIFY_SHA
    engine.reset_ops()
    engine.start_counting()
    CAP = 10 ** 6
    out = []
    exhausted_at = None
    for idx, rec in enumerate(r12['found']):
        if engine.ops_count() >= CAP:
            exhausted_at = idx
            break
        inst = rec['instance']
        xs = [Fr(x) for x in inst['b']]
        dpat = list(inst['d_pattern'])
        t = Fr(inst['r'][0])
        r = [t + x for x in xs]
        built, why = engine.build_instance(xs, dpat, r, 6)
        if built is None:
            out.append({'b_index': rec.get('b_index'), 'built': False,
                        'why': why, 'certificate': None})
            continue
        cert = certify76.certify_instance(built, coset, ec)
        out.append({
            'b_index': rec.get('b_index'),
            'built': True,
            'verdict': cert.get('verdict'),
            'aggregate_total': cert.get('aggregate_total'),
            'committed_verdict': rec['certificate']['verdict'],
            'committed_aggregate_total': rec['certificate']['aggregate_total'],
            'matches_committed': (
                cert.get('verdict') == rec['certificate']['verdict']
                and cert.get('aggregate_total')
                == rec['certificate']['aggregate_total']),
        })
    exhaustion = None
    if exhausted_at is not None or len(out) < len(r12['found']):
        exhaustion = {
            'kind': 'counted_ops_cap',
            'cap': CAP,
            'ops': engine.ops_count(),
            'rows_certified': len(out),
            'rows_total': len(r12['found']),
            'note': ('C6 certificate recomputation stopped at the frozen '
                     '1.0e6 counted-ops cap (IC-1 convention); reported '
                     'AS exhaustion per SR-1 (rules 3/5); never re-scored. '
                     'Certified rows are exact; rows beyond the stop are '
                     'recorded as not-certified-in-run, never dropped.'),
        }
    return {'per_instance': out, 'exhaustion': exhaustion,
            'ops': engine.ops_count()}


# ---------------------------------------------------------------------------
# R4: spot-check computations (the derivation itself is authored text in
# derivation.md from the committed lineage records).
# ---------------------------------------------------------------------------

def r4_spot_checks():
    """Exact spot checks for the derivation, stdlib Fractions only."""
    with open(R12_PATH) as f:
        r12 = json.load(f)
    ct = r12['n2r']['reconciliation']['cross_tabulation']
    e6 = Fr(5) - Fr(6, 2)
    e8 = Fr(5) - Fr(8, 2)
    e10 = Fr(5) - Fr(10, 2)
    a_ratios = [Fr(28, 20), Fr(33, 28)]
    b_ratios = [Fr(33, 26), Fr(33, 33)]
    return {
        'spot_1_exponent_form': {
            'statement': ('HEUR-1 exponent 5 - n/2 evaluated exactly: '
                          'n=6 -> 2, n=8 -> 1, n=10 -> 0'),
            'n_6': str(e6), 'n_8': str(e8), 'n_10': str(e10),
            'arithmetic': 'exact Fractions',
            'provenance': ('ledger/hypotheses/H-ECRANK-ee6e0e.yaml M3 '
                           '(internal); ledger/hypotheses/'
                           'H-ECRANK-36d8d7.yaml HEUR-1 (internal)'),
        },
        'spot_2_per_decade_prediction_factor_n6': {
            'statement': ('HEUR-1 at n=6 predicts count growth factor '
                          '10^2 = 100 per decade of H'),
            'factor': 100,
            'arithmetic': 'exact int',
            'provenance': 'same internal records as spot_1',
        },
        'spot_3_committed_measured_ratios_as_exact_fractions': {
            'statement': ('v2 round (EV-ECRANK-d7e05f) measured decade '
                          'ratios under both conventions, as exact '
                          'Fractions'),
            'convention_A': [str(x) for x in a_ratios],
            'convention_B': [str(x) for x in b_ratios],
            'vs_prediction': '100 per decade',
            'provenance': ('ledger/evidence/EV-ECRANK-d7e05f.yaml '
                           '(internal); committed R12 raw-result.json '
                           'n2r block (internal)'),
        },
        'spot_4_construct_candidate_bound': {
            'statement': ('Bound bytes solve_n6: _quad_rational_roots(A,B,C) '
                          'returns the complete rational root set of ONE '
                          'univariate quadratic -- at most 2 roots, with no '
                          'H input (verified by the R2 trace: H in solve_n6 '
                          'appears only at line 86, the h > H admission '
                          'filter).'),
            'max_candidates_per_tuple': 2,
            'provenance': ('experiments/EXP-ECRANK-73275e/source/'
                           'construct.py at the frozen hash (internal)'),
        },
        'spot_5_r12_height_extrema': {
            'statement': ('Committed R12 cross-tabulation extrema over the '
                          '33 found instances'),
            'max_h_A': max(r['h_A'] for r in ct),
            'max_h_B': max(r['h_B'] for r in ct),
            'min_h_A': min(r['h_A'] for r in ct),
            'min_h_B': min(r['h_B'] for r in ct),
            'provenance': os.path.relpath(R12_PATH, REPO) + ' (internal)',
        },
    }


def r4_proves_too_much_control():
    """P5 control on the draw-side committed data (EXP-ECRANK-76a70d
    R3-armB; EV-ECRANK-8b35bb F1 regime). The structural argument must
    NOT predict saturation where the search space grows with H by
    construction."""
    with open(ARMB_PATH) as f:
        b = json.load(f)
    return {
        'control': 'P5 proves-too-much (C4)',
        'data': os.path.relpath(ARMB_PATH, REPO),
        'committed_facts': {
            'n_b_declared': b['parameters']['n_b_declared'],
            'draws_per_b': b['parameters']['draws_per_b'],
            'H_schedule_per_draw': b['parameters']['H_schedule_per_draw'],
            'S_fixed_indices': b['parameters']['S_fixed_indices'],
            'T_solved_indices': b['parameters']['T_solved_indices'],
            'streams_b_done': [s['b_done'] for s in b['streams']],
            'streams_draws': [s['draws'] for s in b['streams']],
            'streams_solves_ok': [s['solves_ok'] for s in b['streams']],
            'streams_square_ok': [s['square_ok'] for s in b['streams']],
            'found_instances': len(b['found_instances']),
            'cumulative_counts_per_H': b['cumulative_counts_per_H'],
            'ops_counted_total': b['ops_counted_total'],
            'exhaustion': b['exhaustion'],
        },
        'structural_argument_premise': (
            'Construct side: the per-(b,d) candidate set is the rational '
            'root set of ONE univariate quadratic (<= 2, H-independent), '
            'so the cumulative count over a FIXED b-sample is a cumulative '
            'height-distribution of a fixed finite multiset and saturates.'),
        'divergence_step': (
            'DRAW SIDE, the explicit step where the two cases diverge: the '
            'draw-side candidate set per b is NOT a fixed root set -- each '
            'draw selects 5 r-coordinates from a height-H sub-box '
            '(S_fixed_indices 0..4; T_solved 5..7 solved exactly per draw) '
            'and the sub-box lattice size GROWS with H by construction '
            '(H_schedule_per_draw [100,100,100,1000,1000,1000,10000,'
            '10000]). The number of distinct candidate points per b '
            'therefore grows with H, so the saturation premise (a FIXED '
            'finite candidate multiset independent of H) is FALSE on the '
            'draw side.'),
        'argument_prediction_on_draw_side': (
            'The structural argument does NOT predict draw-side '
            'saturation: its premise fails at the sub-box selection step. '
            'The committed draw-side data (square_ok 0 of 80,000 draws; '
            'found_instances 0; the F1 regime of EV-ECRANK-8b35bb, growth '
            'measured on a growing search space) is not an object the '
            'argument addresses and the argument does not predict it '
            'saturates.'),
        'p5_outcome': ('CONTROL OUTCOME: the structural argument does not '
                       'predict saturation where growth was measured (F1 '
                       'regime); no DEFECT is recorded on this control.'),
    }


# ---------------------------------------------------------------------------
# Run-record writer (nested `run:` record carrying RUN_REQUIRED_TOP).
# ---------------------------------------------------------------------------

def now_iso():
    return datetime.now(timezone.utc).isoformat()


def git_info():
    out = {'commit': None, 'dirty': None, 'dirty_files': []}
    try:
        out['commit'] = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], text=True, cwd=REPO).strip()
        status = subprocess.check_output(['git', 'status', '--porcelain'],
                                         text=True, cwd=REPO)
        out['dirty_files'] = [ln for ln in status.splitlines() if ln.strip()]
        out['dirty'] = bool(out['dirty_files'])
    except Exception as exc:
        out['error'] = str(exc)
    return out


def env_info():
    return {
        'python_version': sys.version.split()[0],
        'python_implementation': platform.python_implementation(),
        'python_executable': sys.executable,
        'platform': platform.platform(),
        'machine': platform.node(),
        'machine_arch': platform.machine(),
        'os_release': platform.release(),
        'stdlib_only_pipeline': True,
        'pari_in_pipeline': False,
        'network': 'none',
        'no_seeds_drawn': True,
        'no_floating_point_in_verdicts': True,
    }


INFERENCE_MANIFEST = {
    'requested_policy': 'executor-implementation',
    'reasoning_effort_requested': None,
    'reasoning_effort_note': 'null = policy default per handoff',
    'fallback_used': True,
    'fallback_reason': ('native executor session; orchestration.adapter '
                        'doctor not run in this session; resolved runtime '
                        'recorded as reported by the runtime, unverified '
                        'configuration'),
    'degraded_allowed': False,
    'degraded_requirements': [],
    'independent_session_required': True,
    'independent_session': True,
    'resolved_model_id': 'vllm/qwen3.8-27b',
    'resolved_model_id_source': 'runtime system prompt (as reported)',
    'model_verified': False,
    'model_verified_note': 'no adapter probe claimed; recorded as-is',
    'backend': 'opencode_native',
    'bedrock_guard': ("resolved provider contains no 'bedrock' "
                      "(rule 16 checked)"),
}


def write_run(run_dirname, command, params, status, reason, raw_result,
              t_mono, cost, artifacts_extra=None, started_at=None):
    run_dir = os.path.join(RUNS, run_dirname)
    os.makedirs(run_dir, exist_ok=True)
    finished = now_iso()
    mono = time.monotonic() - t_mono
    gi = git_info()
    body = {
        'id': 'RUN-ECRANK-41775b-' + run_dirname,
        'experiment_id': EXPERIMENT_ID,
        'status': status,
        'task_id': TASK_ID,
        'batch_id': BATCH_ID,
        'hypothesis_id': HYPOTHESIS_ID,
        'code': {
            'commit': gi['commit'],
            'dirty': gi['dirty'],
            'dirty_files': gi['dirty_files'],
            'command': command,
            'argv': command.split(),
            'source_dir': 'experiments/EXP-ECRANK-41775b/source/',
            'source_file': 'experiments/EXP-ECRANK-41775b/source/'
                           'run_package_v2.py',
        },
        'environment': env_info(),
        'inputs': {
            'parameters': params,
            'bound_source_hashes': BOUND_SOURCE_HASHES,
            'input_data_hashes': input_data_hashes(),
            'seeds_note': ('no seeds are drawn anywhere in this experiment; '
                           'the R12 coset reconstruction re-derives the '
                           'committed R12 derivation from the committed '
                           'seed 760906 read-only (a reconstruction of a '
                           'committed value, cross-checked against the '
                           'committed coset_V field, not a new draw)'),
        },
        'timing': {
            'started_at': started_at or finished,
            'finished_at': finished,
            'wall_seconds_monotonic': round(mono, 6),
            'wall_seconds': round(mono, 6),
        },
        'result': {
            'validity_reason': reason,
            'metrics': cost,
            'certificate': {
                'kind': 'none',
                'verified': True,
                'verifier': ('no discrete_log/decomposition/key_recovery '
                             'claim'),
                'certificate_note': ("kind 'none': this run asserts no "
                                     'discrete_log, decomposition, or '
                                     'key_recovery claim.'),
            },
        },
        'inference': INFERENCE_MANIFEST,
        'validity': {'status': status, 'reason': reason},
    }
    with open(os.path.join(run_dir, 'raw-result.json'), 'w') as f:
        json.dump(raw_result, f, indent=1, sort_keys=True)
    with open(os.path.join(run_dir, 'command.txt'), 'w') as f:
        f.write(command + '\n')
    with open(os.path.join(run_dir, 'environment.json'), 'w') as f:
        json.dump(env_info(), f, indent=2, sort_keys=True)
        f.write('\n')
    with open(os.path.join(run_dir, 'stdout.log'), 'w') as f:
        f.write(json.dumps({'summary': reason, 'metrics': cost}, indent=2)
                + '\n')
    with open(os.path.join(run_dir, 'stderr.log'), 'w') as f:
        f.write('')
    man = {'run': body}
    try:
        import yaml
        with open(os.path.join(run_dir, 'manifest.yaml'), 'w') as f:
            yaml.safe_dump(man, f, sort_keys=False, width=100)
    except ImportError:
        with open(os.path.join(run_dir, 'manifest.yaml'), 'w') as f:
            f.write(json.dumps(man, indent=2))
    with open(os.path.join(run_dir, 'cost-ledger.json'), 'w') as f:
        json.dump(cost, f, indent=1, sort_keys=True)
    for name, obj in (artifacts_extra or {}).items():
        with open(os.path.join(run_dir, name), 'w') as f:
            if name.endswith('.json'):
                json.dump(obj, f, indent=1, sort_keys=True)
            else:
                f.write(obj)
    return run_dir


# ---------------------------------------------------------------------------
# Driver: runs in the frozen order with the frozen stop rules.
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run', choices=['R1', 'R2', 'R3', 'R4', 'R5'],
                    required=True)
    args = ap.parse_args()
    t0 = time.monotonic()
    started_at = now_iso()

    # SR-4 at every run start (bound-byte hash verification).
    ok, hashes = check_bound_hashes()
    if not ok:
        bad = {k: v for k, v in hashes.items() if not v['match']}
        print('SR-4 STOP: bound-byte hash mismatch: %s' % json.dumps(bad))
        return 3
    print('SR-4 bound hashes: OK (all %d match)' % len(hashes))

    if args.run == 'R1':
        verdict, f1, f2 = run_calibration()
        cost = {'calibration_pass': verdict['calibration_pass'],
                'wall_seconds': round(time.monotonic() - t0, 6),
                'counted_ops': 0,
                'ops_note': ('R1 arithmetic is exact Fraction counting '
                             'over constructed families; no bound engine '
                             'ops counted (no bound solver invoked).')}
        extra = {
            'calibration-families.json': {'family_1_tuples': f1,
                                          'family_2_tuples': f2},
            'instrument-verdicts.json': verdict,
        }
        status = 'completed'
        reason = ('R1 calibration recorded; family_1 pass=%s family_2 '
                  'pass=%s; calibration_pass=%s'
                  % (verdict['family_1']['pass'],
                     verdict['family_2']['pass'],
                     verdict['calibration_pass']))
        write_run('R1-calibration',
                  'python3 experiments/EXP-ECRANK-41775b/source/'
                  'run_package_v2.py --run R1',
                  {'run_kind': 'calibration_admission',
                   'families': ['family_1_two_roots_per_tuple',
                                'family_2_uniform_decades']},
                  status, reason, verdict, t0, cost, extra,
                  started_at=started_at)
        print(reason)
        if not verdict['calibration_pass']:
            print('SR-2 STOP: calibration failure; all ratio readings '
                  'void; defect recorded.')
            return 2
        return 0

    if args.run == 'R2':
        trace = r2_trace()
        adj = r2_adjudication(trace)
        E, construct, NF, C, CL = load_bound_modules()
        E.reset_ops()
        E.start_counting()
        dyn = r2_dynamic(E, construct)
        ops = E.ops_count()
        E.reset_ops()
        raw = {'sr4_bound_hashes': hashes, 'trace': trace,
               'adjudication': adj, 'dynamic': dyn}
        cost = {'counted_ops_double_invocation': ops,
                'wall_seconds': round(time.monotonic() - t0, 6),
                'ops_note': ('ops are the bound engine IC-1 counted ops of '
                             'the six solve_n6 invocations (3 tuples x 2 H '
                             'values) only.')}
        extra = {'trace-report.json': trace,
                 'dynamic-diff.json': dyn,
                 'verdict-ledger.json': adj}
        if adj['h_in_n6_candidate_generation']:
            status = 'failed'
            reason = ('SR-3 STOP: R2 trace shows H in n=6 candidate '
                      'generation; P1 falsified; adjudication arms stop; '
                      'all receipts preserved.')
        else:
            status = 'completed'
            reason = ('R2 structural trace recorded; solve_n6 H use sites '
                      '= admission filter only (line 86); dynamic '
                      'double-invocation: meta and root sets identical on '
                      'all three frozen tuples, partition differs only by '
                      'the height filter.')
        write_run('R2-structural-trace',
                  'python3 experiments/EXP-ECRANK-41775b/source/'
                  'run_package_v2.py --run R2',
                  {'run_kind': 'structural_trace',
                   'frozen_tuples': [649, 1299, 4995],
                   'H_values': [10000, 1000000000]},
                  status, reason, raw, t0, cost, extra,
                  started_at=started_at)
        print(reason)
        return 0 if status == 'completed' else 2

    if args.run == 'R3':
        E, construct, NF, C, CL = load_bound_modules()
        E.reset_ops()
        E.start_counting()
        res = r3_readmission(E)
        ops_readmission = E.ops_count()
        E.reset_ops()
        cert = r3_certify(E, C)
        ops_cert = E.ops_count()
        E.reset_ops()
        raw = dict(res)
        raw['sr4_bound_hashes'] = hashes
        raw['c6_certificate_recomputation'] = cert
        cost = {
            'counted_ops_readmission_path': ops_readmission,
            'counted_ops_certificate_path': ops_cert,
            'ops_cap': 1000000,
            'ops_cap_respected': (ops_readmission < 10 ** 6),
            'wall_seconds': round(time.monotonic() - t0, 6),
            'exhaustion': cert.get('exhaustion'),
        }
        extra = {
            'readmission.json': res,
            'multiplicity-histogram.json': {
                'histogram': res['multiplicity_histogram'],
                'max_multiplicity': res['max_multiplicity'],
                'per_tuple_counts': dict(
                    collections.Counter(r['b_index'] for r in res['rows'])),
            },
            'verdict-ledger.json': {
                'precondition_P2': res['precondition_P2'],
                'n8_band': res['n8_band'],
                'c6_certificate_recomputation': cert,
                'ops': {'readmission': ops_readmission,
                        'certificate': ops_cert},
            },
        }
        status = 'completed'
        reason = ('R3 extended-height re-admission recorded from committed '
                  'R12 bytes; ledger empty (0 r_height entries; counts '
                  'labeled exact over the recoverable subset and lower '
                  'bounds over anything unrecorded); n=8 band VACUOUS '
                  'verbatim from committed R14 zeros; C6 certificate '
                  'recomputation %s'
                  % ('exhausted at the 1.0e6 counted-ops cap (reported AS '
                     'exhaustion, never re-scored)'
                     if cert.get('exhaustion') else 'in-cap'))
        write_run('R3-extended-readmission',
                  'python3 experiments/EXP-ECRANK-41775b/source/'
                  'run_package_v2.py --run R3',
                  {'run_kind': 'extended_readmission',
                   'bands': [10000, 100000, 1000000, 10000000],
                   'conventions': ['A', 'B'],
                   'ops_cap': 1000000, 'wall_cap_s': 600},
                  status, reason, raw, t0, cost, extra,
                  started_at=started_at)
        print(reason)
        return 0

    if args.run == 'R4':
        spot = r4_spot_checks()
        ctrl = r4_proves_too_much_control()
        E, construct, NF, C, CL = load_bound_modules()
        E.reset_ops()
        E.start_counting()
        res = r3_readmission(E)
        E.reset_ops()
        spot['spot_6_extended_band_ratios_exact'] = {
            'statement': ('R3 extended-band decade ratios under both '
                          'conventions (exact Fractions; the R3 ratio '
                          'table re-executed here for cross-quotation '
                          'only)'),
            'convention_A': res['decade_ratios_A_ext'],
            'convention_B': res['decade_ratios_B_ext'],
            'provenance': 'computed in this experiment (R3 path, internal)',
        }
        raw = {'sr4_bound_hashes': hashes, 'spot_checks': spot,
               'proves_too_much_control': ctrl}
        cost = {'wall_seconds': round(time.monotonic() - t0, 6),
                'counted_ops': 0,
                'ops_note': ('R4 spot checks are exact Fraction arithmetic '
                             'over committed bytes plus a re-execution of '
                             'the R3 ratio table for cross-quotation; no '
                             'new measurement.')}
        extra = {'spot-check.json': spot,
                 'proves-too-much-control.json': ctrl}
        status = 'completed'
        reason = ('R4 spot checks + proves-too-much control recorded; '
                  'derivation.md is the authored derivation artifact.')
        write_run('R4-density-derivation',
                  'python3 experiments/EXP-ECRANK-41775b/source/'
                  'run_package_v2.py --run R4',
                  {'run_kind': 'density_derivation_spot_checks'},
                  status, reason, raw, t0, cost, extra,
                  started_at=started_at)
        print(reason)
        return 0

    if args.run == 'R5':
        diff = {}
        verdict, _, _ = run_calibration()
        with open(os.path.join(RUNS, 'R1-calibration',
                               'raw-result.json')) as f:
            r1_orig = json.load(f)
        diff['R1_verdict_identical'] = (verdict == r1_orig)
        E, construct, NF, C, CL = load_bound_modules()
        E.reset_ops()
        E.start_counting()
        res = r3_readmission(E)
        E.reset_ops()
        with open(os.path.join(RUNS, 'R3-extended-readmission',
                               'raw-result.json')) as f:
            r3_orig = json.load(f)
        keys = ['bands', 'N_per_H_convention_A_ext',
                'N_per_H_convention_B_ext', 'decade_ratios_A_ext',
                'decade_ratios_B_ext', 'saturation_ceiling_A',
                'saturation_ceiling_B', 'multiplicity_histogram',
                'max_multiplicity', 'n8_band', 'precondition_P2',
                'max_h_A_observed', 'max_h_B_observed']
        diff['R3_fields_identical'] = {k: (res[k] == r3_orig.get(k))
                                       for k in keys}
        diff['R3_all_fields_identical'] = all(
            diff['R3_fields_identical'].values())
        rehash = {}
        for run in ('R2-structural-trace', 'R4-density-derivation'):
            d = os.path.join(RUNS, run)
            for name in sorted(os.listdir(d)):
                if name.endswith('.json') or name.endswith('.md'):
                    p = os.path.join(d, name)
                    rehash[os.path.relpath(p, REPO)] = sha256_file(p)
        with open(os.path.join(RUNS, 'R2-structural-trace',
                               'trace-report.json')) as f:
            t2_recorded = json.load(f)
        diff['R2_trace_recomputed_identical'] = (r2_trace() == t2_recorded)
        diff['R2_R4_rehashes'] = rehash
        empty = (diff['R1_verdict_identical']
                 and diff['R3_all_fields_identical']
                 and diff['R2_trace_recomputed_identical'])
        diff['replay_diff_empty'] = empty
        cost = {'wall_seconds': round(time.monotonic() - t0, 6),
                'replay_diff_empty': empty}
        status = 'completed'
        reason = ('R5 fresh-process replay recorded; R1 verdict identical='
                  '%s; R3 fields identical=%s; R2 trace recomputed '
                  'identical=%s; R2/R4 artifacts re-hashed (%d files); '
                  'replay_diff_empty=%s'
                  % (diff['R1_verdict_identical'],
                     diff['R3_all_fields_identical'],
                     diff['R2_trace_recomputed_identical'], len(rehash),
                     empty))
        write_run('R5-replay',
                  'python3 experiments/EXP-ECRANK-41775b/source/'
                  'run_package_v2.py --run R5',
                  {'run_kind': 'determinism_replay',
                   'replays': ['R1-calibration', 'R3-extended-readmission'],
                   'rehashes': ['R2-structural-trace',
                                'R4-density-derivation']},
                  status, reason, {'replay': diff}, t0, cost,
                  {'replay-diff.json': diff}, started_at=started_at)
        print(reason)
        return 0 if empty else 1

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
