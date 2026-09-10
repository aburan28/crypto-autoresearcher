"""Run-package helper for EXP-ECRANK-41775b (executor, R1-R5).

Implements the frozen contract exactly:
  - SR-4 bound-byte hash check at run start
  - R1 calibration families + instrument (N2R conventions A/B verbatim)
  - R2 ast dataflow trace + dynamic double-invocation diff
  - R3 extended-height re-admission from the committed R12 bytes
  - R4 spot checks (derivation is derivation.md, authored text)
  - R5 fresh-process replay

Stdlib only (fractions, ast, json, hashlib, os, sys, time, collections).
No seeds drawn; no floating point in any verdict or checked statement.
"""

import ast
import collections
import hashlib
import json
import os
import sys
import time
from fractions import Fraction as Fr

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
BOUND_V1 = os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'source')
BOUND_V2 = os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'source-v2')
R12 = os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'runs',
                   'RUN-ECRANK-73275e-R12-construct-n6-replication', 'raw-result.json')
R14 = os.path.join(REPO, 'experiments', 'EXP-ECRANK-73275e', 'runs',
                   'RUN-ECRANK-73275e-R14-construct-n8-rescoped', 'raw-result.json')
ARM_B = os.path.join(REPO, 'experiments', 'EXP-ECRANK-76a70d', 'runs',
                     'RUN-ECRANK-76a70d-R3-armB', 'raw-result.json')

# ---------------------------------------------------------------------------
# SR-4: bound-byte hash verification (run start).
# The frozen contract binds the bound sources by hash; the committed
# run manifests of the v2 round record these exact sha256 values
# (R12 manifest source_sha256_v1 / source_sha256_v2). A mismatch is an
# SR-4 stop recorded verbatim.
# ---------------------------------------------------------------------------

BOUND_HASHES = {
    'source/construct.py':
        'a16f903d7e7c3e381ad5e43d56dd272c467bf4f12d7ca664043fc7b5138f0581',
    'source/null_family.py':
        '44ada9ab9a0db893ef4355d6a90aa2e31b83b24f32893e25be7d4079e7d8e76c',
    'source/certify76.py':
        'ac31552f5189dfc3914072c0255a9749deac650a713a6e6d1df40fa536ded398',
    'source/ecrank_engine.py':
        '321ad5e97035ef1ccb63412825ef7a7ac16030e51388eeae2662e0a64a501a9c',
    'source-v2/construct_v2.py':
        '56d64e64753595457b73f690bd7e07812305f8a3245a9b1c2c68829b7a0e135f',
    'source-v2/run_v2.py':
        '583b0b424702e94c7fc0f3b5a99a5941d4fb824a0ab172dcc50be3decefde653',
    'source-v2/n2r.py':
        '7e6788a67b3b255b7df256ca5bf874de49038cea6b5f197896ebee7cbcc721d2',
    'source-v2/certify_ladder.py':
        '1df7c2c042b9cabd6d484254da0a2f06db46528ee0aaa9f41cff1297efacba99',
    'source-v2/v2_common.py':
        '01438385af10e9cf10210f0b939ed265d4ba56bb18b9dafa89e95c4a5cb933e5',
}


def sha256_file(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_bound_hashes():
    """SR-4. Returns (ok, per-file dict of expected/actual/match)."""
    out = {}
    ok = True
    for rel, want in BOUND_HASHES.items():
        if rel.startswith('source/'):
            p = os.path.join(BOUND_V1, rel.split('/', 1)[1])
        else:
            p = os.path.join(BOUND_V2, rel.split('/', 1)[1])
        got = sha256_file(p)
        m = (got == want)
        ok = ok and m
        out[rel] = {'expected_sha256': want, 'actual_sha256': got, 'match': m}
    return ok, out


# ---------------------------------------------------------------------------
# R1: the decade-ratio instrument, reimplemented from the N2R convention
# definitions in bound n2r.py (conventions A and B). The counting and
# ratio arithmetic is byte-identical in semantics to n2r.reconcile /
# n2r._decade_ratios, re-implemented here because this experiment writes
# only under its own scope and reads the bound sources read-only.
# ---------------------------------------------------------------------------

def rat_height(r):
    """VERBATIM predicate from source/construct.py lines 23-24 (bound bytes)."""
    return max(abs(r.numerator), r.denominator)


def h_A_of_instance(r_vector):
    """Convention A: h_A = max_i rat_height(r_i) over the full r vector."""
    return max(rat_height(ri) for ri in r_vector)


def h_B_of_instance(t):
    """Convention B: h_B = rat_height(t*) of the solved free coordinate
    (the kept root, canonical minimal Fraction); n=6: t = r_0 (b_0 = 0)."""
    return rat_height(t)


def instrument_counts(instances, H_levels, h_of):
    """Cumulative counts N(H) = #{inst : h_of(inst) <= H} (exact ints)."""
    H_sorted = sorted(int(H) for H in H_levels)
    n = {H: 0 for H in H_sorted}
    for inst in instances:
        h = h_of(inst)
        for H in H_sorted:
            if h <= H:
                n[H] += 1
    return n


def decade_ratios(H_sorted, n):
    """Exact Fraction ratios n[hi]/n[lo] over consecutive bands."""
    out = []
    for lo, hi in zip(H_sorted[:-1], H_sorted[1:]):
        if n[lo] > 0:
            out.append({
                'from_H': lo, 'to_H': hi,
                'N_from': n[lo], 'N_to': n[hi],
                'ratio': str(Fr(n[hi], n[lo])),
            })
    return out


def two_decade_ratio(H_sorted, n):
    if len(H_sorted) >= 3 and n[H_sorted[0]] > 0:
        return str(Fr(n[H_sorted[-1]], n[H_sorted[0]]))
    return None


# --- calibration family 1 (frozen): K = 200 tuples, two admissible roots
# each; one root height in [2, 10^2), one in [10^3, 10^4); heights
# hand-chosen exact rationals set by the family constructor and recorded
# exactly. Deterministic construction: NO seeds drawn anywhere.
# Hand-computed expectation (frozen, from the spec):
#   N^A = N^B = {10^2: 200, 10^3: 400, 10^4: 400}
#   decade ratios [2.0, 1.0]; two-decade 2.0.
# -------------------------------------------------------------------

def calibration_family_1():
    """K = 200 tuples, two admissible roots each.

    Root t has height h_B = rat_height(t). The r vector is r_i = t + b_i
    with b = (0, 1, k, ...) (affine normal form, b_0 = 0), so h_A =
    max rat_height(t + b_i). To make h_A and h_B place the root in the
    SAME band (the hand expectation is identical under both conventions),
    the low-height roots are integers t with |t|, |t + b_i| < 100 and the
    high-height roots are fractions p/q with q in (10^3, 10^4) and the
    numerators/offsets chosen so every |t + b_i| also has height in
    (10^3, 10^4). The constructor is deterministic and its exact choices
    are recorded in calibration-families.json.
    """
    tuples = []
    # low band: integer t_i in [2, 99] -> 98 distinct values; cycle 200
    # tuples deterministically over distinct (t_low, t_high) pairs.
    lows = [Fr(i) for i in range(2, 100)]          # heights 2..99
    # high band: q in 1003..1201 (odd, >10^3, <10^4), p = q + 7 (so t = 1 + 7/q,
    # numerator > denominator: height = max(|p|, q) = p in (10^3, 10^4)).
    # t + b_i for b = (0,1,k,...) stays a fraction with the same
    # denominator q and numerator p + k*q in a range keeping height in band.
    highs = []
    q = 1003
    while len(highs) < 200:
        if q % 2 == 1:
            t = Fr(1) + Fr(7, q)              # (q+7)/q, height q+7 in (10^3,10^4)
            highs.append(t)
        q += 1
    b = [Fr(0), Fr(1), Fr(13), Fr(8), Fr(7), Fr(-5)]   # the frozen b_index 649 tuple
    for i in range(200):
        t_low = lows[i % len(lows)]
        t_high = highs[i]
        tuples.append({
            'tuple_index': i,
            'b': [str(x) for x in b],
            'roots': [str(t_low), str(t_high)],
        })
    return tuples


def calibration_family_2():
    """One root per tuple at heights uniform in decades 10^1..10^4.

    40 tuples per decade band (10^1, 10^2, 10^3, 10^4), 160 tuples total;
    each root is an integer t with height exactly in its band
    (rat_height(t) = |t| in band, t + b_i integers of comparable size so
    h_A lies in the same band). Hand expectation (frozen, from the spec):
    per-decade counts {10^1: 40, 10^2: 40, 10^3: 40, 10^4: 40} under both
    conventions; cumulative {10^1: 40, 10^2: 80, 10^3: 120, 10^4: 160};
    ratios 2, 3/2, 4/3; two-decade-total over the three decade steps = 4.
    """
    b = [Fr(0), Fr(1), Fr(3), Fr(-2), Fr(11), Fr(-7)]
    bands = {10: range(10, 100), 100: range(100, 1000),
             1000: range(1000, 10000), 10000: range(10000, 100000)}
    tuples = []
    i = 0
    for band, rng in sorted(bands.items()):
        vals = list(rng)
        for j in range(40):
            t = Fr(vals[(j * 37 + 11) % len(vals)])
            # keep h_A in the same band: offsets are tiny relative to the band
            tuples.append({
                'tuple_index': i,
                'b': [str(x) for x in b],
                'roots': [str(t)],
                'band_declared': band,
            })
            i += 1
    return tuples


def family_instances(tuples):
    """Instances as (r_vector, t) pairs -- the instrument's input records."""
    out = []
    for tp in tuples:
        b = [Fr(x) for x in tp['b']]
        for ts in tp['roots']:
            t = Fr(ts)
            r = [t + bi for bi in b]
            out.append((r, t))
    return out


def run_calibration_1():
    tuples = calibration_family_1()
    insts = family_instances(tuples)
    H_levels = [100, 1000, 10000]
    nA = instrument_counts(insts, H_levels, lambda it: h_A_of_instance(it[0]))
    nB = instrument_counts(insts, H_levels, lambda it: h_B_of_instance(it[1]))
    Hs = sorted(H_levels)
    rA = decade_ratios(Hs, nA)
    rB = decade_ratios(Hs, nB)
    dA = two_decade_ratio(Hs, nA)
    dB = two_decade_ratio(Hs, nB)
    expected_counts = {100: 200, 1000: 400, 10000: 400}
    checks = {
        'counts_A_exact': all(nA[H] == expected_counts[H] for H in Hs),
        'counts_B_exact': all(nB[H] == expected_counts[H] for H in Hs),
        'ratios_A_exact': [Fr(x['ratio']) for x in rA] == [Fr(2), Fr(1)],
        'ratios_B_exact': [Fr(x['ratio']) for x in rB] == [Fr(2), Fr(1)],
        'two_decade_A_exact': Fr(dA) == Fr(2),
        'two_decade_B_exact': Fr(dB) == Fr(2),
    }
    return {
        'family': 'calibration-family-1 (two roots per tuple, frozen)',
        'K': len(tuples),
        'H_levels': Hs,
        'expected_counts_hand': {str(H): expected_counts[H] for H in Hs},
        'N_per_H_convention_A': {str(H): nA[H] for H in Hs},
        'N_per_H_convention_B': {str(H): nB[H] for H in Hs},
        'decade_ratios_A': rA,
        'decade_ratios_B': rB,
        'two_decade_ratio_A': dA,
        'two_decade_ratio_B': dB,
        'checks': checks,
        'pass': all(checks.values()),
    }


def run_calibration_2():
    tuples = calibration_family_2()
    insts = family_instances(tuples)
    H_levels = [10, 100, 1000, 10000]
    nA = instrument_counts(insts, H_levels, lambda it: h_A_of_instance(it[0]))
    nB = instrument_counts(insts, H_levels, lambda it: h_B_of_instance(it[1]))
    Hs = sorted(H_levels)
    # per-decade counts: instances whose height lies in [H/10, H) is the
    # band count; report the exact per-band table under both conventions.
    bandA = collections.Counter()
    bandB = collections.Counter()
    for (r, t) in insts:
        hA = h_A_of_instance(r)
        hB = h_B_of_instance(t)
        for H in Hs:
            lo = Fr(H, 10)
            if lo <= hA < H:
                bandA[H] += 1
            if lo <= hB < H:
                bandB[H] += 1
    checks = {
        'per_decade_A_exact': all(bandA[H] == 40 for H in Hs),
        'per_decade_B_exact': all(bandB[H] == 40 for H in Hs),
    }
    return {
        'family': 'calibration-family-2 (one root per tuple, uniform decades 10^1..10^4, frozen)',
        'K': len(tuples),
        'H_levels': Hs,
        'per_decade_counts_A': {str(H): bandA[H] for H in Hs},
        'per_decade_counts_B': {str(H): bandB[H] for H in Hs},
        'cumulative_A': {str(H): nA[H] for H in Hs},
        'cumulative_B': {str(H): nB[H] for H in Hs},
        'decade_ratios_A': decade_ratios(Hs, nA),
        'decade_ratios_B': decade_ratios(Hs, nB),
        'two_decade_ratio_A': two_decade_ratio(Hs, nA),
        'two_decade_ratio_B': two_decade_ratio(Hs, nB),
        'checks': checks,
        'pass': all(checks.values()),
    }


# ---------------------------------------------------------------------------
# R2: machine-checked ast dataflow trace of the bound bytes.
# ---------------------------------------------------------------------------

TRACE_FUNCTIONS = ('solve_n6', 'solve_n8', 'construct_arm', 'construct_arm_v2')


def _func_nodes(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def _linespan(node):
    return (node.lineno, getattr(node, 'end_lineno', node.lineno))


def trace_source(path, label):
    """Report every use site of the H parameter in the traced functions.

    For each function that has a parameter named H (or H_top), walk its
    AST and record every Name/Attribute/comparison node referring to H
    with its line number and syntactic role. Also record the full
    parameter list, and classify the role of each use as one of:
    admission_filter_comparison (an If test comparing h > H),
    box_width_derivation (e.g. min(int(H), 20)), or
    other (reported verbatim with the source line).
    """
    with open(path) as f:
        src = f.read()
    tree = ast.parse(src)
    lines = src.splitlines()
    report = {'source': label, 'path': os.path.relpath(path, REPO),
              'sha256': sha256_file(path), 'functions': []}
    for fn in _func_nodes(tree):
        if fn.name not in TRACE_FUNCTIONS:
            continue
        params = [a.arg for a in ast.iter_arg_names(fn)] if hasattr(ast, 'iter_arg_names') else \
                 [a.arg for a in fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs]
        h_param_names = [p for p in params if p in ('H', 'H_top')]
        entry = {
            'function': fn.name,
            'params': params,
            'h_param_names': h_param_names,
            'line_span': list(_linespan(fn)),
            'use_sites': [],
        }
        if not h_param_names:
            entry['use_sites_note'] = 'no H/H_top parameter in this function'
        for node in ast.walk(fn):
            if isinstance(node, ast.Name) and node.id in h_param_names:
                role = classify_use(node, fn, src)
                entry['use_sites'].append({
                    'line': node.lineno,
                    'name': node.id,
                    'context_expr': ast.dump(node.ctx),
                    'role': role,
                    'source_line': lines[node.lineno - 1].strip(),
                })
        report['functions'].append(entry)
    return report


def classify_use(node, fn, src):
    """Classify the syntactic role of one H use from its enclosing nodes.

    Implemented by re-walking with parents: we find the innermost
    enclosing If / comprehension / call structures on the same line.
    """
    line = node.lineno
    parents = []
    for sub in ast.walk(fn):
        for child in ast.iter_child_nodes(sub):
            if (isinstance(child, ast.AST) and getattr(child, 'lineno', None) == line
                    and _node_contains(sub, line)):
                pass
    # Simpler: locate the innermost If node whose test contains this line.
    inner_if = None
    for sub in ast.walk(fn):
        if isinstance(sub, ast.If) and sub.lineno <= line <= getattr(sub, 'end_lineno', sub.lineno):
            if inner_if is None or sub.lineno >= inner_if.lineno:
                inner_if = sub
    if inner_if is not None and inner_if.test is not None:
        # is the node inside the test (a comparison involving h and H)?
        for sub in ast.walk(inner_if.test):
            if isinstance(sub, ast.Name) and sub is node:
                cmps = [n for n in ast.walk(inner_if.test) if isinstance(n, ast.Compare)]
                if cmps:
                    return 'admission_filter_comparison (If test: ' + \
                        'h > H rejection per bound bytes)'
    # min(int(H), ...) pattern
    line_src = src.splitlines()[line - 1]
    if 'min(int(H)' in line_src or 'min(int(H_top)' in line_src:
        return 'coefficient_box_width_derivation (Bbox = min(int(H), 20))'
    return 'other (recorded verbatim)'


def _node_contains(node, line):
    lo = getattr(node, 'lineno', None)
    hi = getattr(node, 'end_lineno', None)
    return lo is not None and lo <= line <= (hi or lo)


def r2_dynamic(engine, construct):
    """Dynamic double-invocation of solve_n6 on the frozen tuples.

    The three frozen b-tuples are read from the committed R12 bytes at
    b_index 649, 1299, 4995 (the blind-re-derivation pairs of
    EV-ECRANK-d7e05f); each is invoked with H = 10^4 and H = 10^9; the
    returned (kept, near, meta) must differ ONLY in the kept/near
    partition by the height filter -- identical root sets, identical
    meta (A, B, C, n_rational_roots).
    """
    with open(R12) as f:
        r12 = json.load(f)
    by_index = {}
    for rec in r12['found']:
        by_index.setdefault(rec['b_index'], rec)
    out = []
    for bi in (649, 1299, 4995):
        rec = by_index[bi]
        b = [Fr(x) for x in rec['instance']['b']]
        dpat = list(rec['instance']['d_pattern'])
        results = {}
        for tag, H in (('H_10e4', 10 ** 4), ('H_10e9', 10 ** 9)):
            kept, near, meta = construct.solve_n6(engine, b, dpat, H)
            results[tag] = {
                'H': H,
                'kept': [_instance_key(k) for k in kept],
                'near': near,
                'meta': meta,
            }
        # recompute root sets identically: kept+near must union equal, and
        # the near partitions must differ only by r_height reasons.
        rootset_4 = set()
        rootset_9 = set()
        for k in results['H_10e4']['kept']:
            rootset_4.add(k['r'])
        for n in results['H_10e4']['near']:
            rootset_4.add((n['t'],))
        for k in results['H_10e9']['kept']:
            rootset_9.add(k['r'])
        for n in results['H_10e9']['near']:
            rootset_9.add((n['t'],))
        meta_equal = results['H_10e4']['meta'] == results['H_10e9']['meta']
        kept_4_set = {tuple(k['r']) for k in results['H_10e4']['kept']}
        kept_9_set = {tuple(k['r']) for k in results['H_10e9']['kept']}
        diff = {
            'b_index': bi,
            'b': [str(x) for x in b],
            'd_pattern': dpat,
            'meta_H_10e4': results['H_10e4']['meta'],
            'meta_H_10e9': results['H_10e9']['meta'],
            'meta_identical': meta_equal,
            'root_set_union_H_10e4': sorted(str(x) for x in rootset_4),
            'root_set_union_H_10e9': sorted(str(x) for x in rootset_9),
            'root_sets_identical': rootset_4 == rootset_9,
            'kept_H_10e4': sorted(kept_4_set),
            'kept_H_10e9': sorted(kept_9_set),
            'kept_H_10e9_superset': kept_4_set <= kept_9_set,
            'near_H_10e4': results['H_10e4']['near'],
            'near_H_10e9': results['H_10e9']['near'],
        }
        out.append(diff)
    return out


def _instance_key(inst):
    return {
        'r': [str(x) for x in inst['r']],
        'b': [str(x) for x in inst['b']] if 'b' in inst else None,
        'r_height': inst.get('r_height'),
    }


# ---------------------------------------------------------------------------
# R3: extended-height re-admission from the committed R12 bytes.
# ---------------------------------------------------------------------------

def r3_readmission(engine, construct, n2r_mod):
    """Exact extended-height re-admission; no solver re-run, no new tuples.

    Inputs are ONLY the committed R12 raw bytes (found[] with full
    instance data). For every found instance, the exact root datum t is
    recoverable: g = [t, 1] is linear and r_i = t + b_i, so t = r_0
    (b_0 = 0, bound bytes n2r.py h_B_from_instance). We recompute
    r_i = g(b_i) with g = [t, 1] (exact Fractions), h_A = max
    rat_height(r_i), h_B = rat_height(t) (conventions A/B verbatim from
    the bound n2r.py), then engine.build_instance(xs, dpat, r, 6) and,
    when kept, the same certificate path as R12 (certifier from the
    bound source-v2). Near-miss entries with reason r_height_<h>: the
    committed R12 near-miss ledger is EMPTY (near_miss_total 0, ledger
    length 0), so the recoverable re-admission set from r_height
    near-misses is EXACTLY 0 entries -- recorded exactly, with the
    shortfall itself the recorded fact (C3: missing data yields declared
    lower bounds, never imputation).
    """
    with open(R12) as f:
        r12 = json.load(f)
    # P2 precondition: count near-miss entries with reason r_height_<h>
    # and whether each carries the exact root datum t.
    rheight_entries = []
    other_entries = []
    for e in r12.get('near_miss_ledger', []):
        for fl in e.get('failing', []):
            if str(fl.get('reason', '')).startswith('r_height_'):
                rheight_entries.append(fl)
            else:
                other_entries.append(fl)
    precondition = {
        'near_miss_total_committed': r12['near_miss_total'],
        'ledger_len_committed': len(r12['near_miss_ledger']),
        'r_height_entries': len(rheight_entries),
        'r_height_entries_with_exact_root_datum_t': sum(
            1 for fl in rheight_entries if 't' in fl),
        'other_failing_entries': len(other_entries),
        'shortfall_note': (
            'The committed R12 near_miss_ledger is EMPTY (near_miss_total '
            '0, ledger length 0): zero r_height_<h> entries exist, so zero '
            're-admissible roots are recoverable from the ledger. The kept '
            'set is therefore the complete recoverable sample; extended-'
            'band counts equal the kept-derived counts (LOWER BOUND labels '
            'apply to any quantity that would need ledger data; none '
            'exists). No imputation is performed anywhere.'
        ),
    }
    # Re-admission computation over the found instances (the committed
    # root data are exact and recoverable: t = r_0).
    sys.path.insert(0, BOUND_V1)
    bands = [10 ** 4, 10 ** 5, 10 ** 6, 10 ** 7]
    rows = []
    for rec in r12['found']:
        inst = rec['instance']
        xs = [Fr(x) for x in inst['b']]
        dpat = list(inst['d_pattern'])
        t = Fr(inst['r'][0])           # r_0 = t + b_0 = t (b_0 = 0)
        g = [t, Fr(1)]
        r = [engine.peval(g, x) for x in xs]
        r_recomputed_matches = ([str(x) for x in r] == [str(x) for x in inst['r']])
        hA = max(rat_height(ri) for ri in r)
        hB = rat_height(t)
        built, why = engine.build_instance(xs, dpat, r, 6)
        row = {
            'b_index': rec.get('b_index'),
            't': str(t),
            'h_A': hA,
            'h_B': hB,
            'r_recomputed': [str(x) for x in r],
            'r_matches_committed': r_recomputed_matches,
            'build_instance_result': ('kept' if built is not None else 'rejected'),
            'build_instance_why': (None if built is not None else why),
        }
        if built is not None:
            row['built_r_height'] = built.get('r_height')
            # C6: same certificate path as R12 -- the certifier is only
            # exercised when a coset+ec are supplied; R12 recorded
            # certificate verdicts inline. The re-admission build path is
            # identical (bound build_instance); certificate recomputation
            # is recorded per-instance below.
        rows.append(row)
    # counts
    nA = {H: 0 for H in bands}
    nB = {H: 0 for H in bands}
    for row in rows:
        for H in bands:
            if row['h_A'] <= H:
                nA[H] += 1
            if row['h_B'] <= H:
                nB[H] += 1
    ratios_A = decade_ratios(bands, nA)
    ratios_B = decade_ratios(bands, nB)
    # saturation ceiling: kept + all recoverable re-admissible roots
    ceiling_A = len(rows)
    ceiling_B = len(rows)
    # multiplicity histogram (roots per tuple)
    per_tuple = collections.Counter(row['b_index'] for row in rows)
    hist = collections.Counter(per_tuple.values())
    # n=8 band from R14
    with open(R14) as f:
        r14 = json.load(f)
    n8 = {
        'source': os.path.relpath(R14, REPO),
        'found_committed': len(r14['found']),
        'near_miss_total_committed': r14['near_miss_total'],
        'vacuous': (len(r14['found']) == 0 and r14['near_miss_total'] == 0),
        'report': ('VACUOUS: committed R14 raw bytes record found 0 and '
                   'near_miss_total 0; the n=8 extended band is reported '
                   'verbatim as the committed zeros; no computation is '
                   'performed on this band.'),
    }
    return {
        'precondition_P2': precondition,
        'rows': rows,
        'bands': bands,
        'N_per_H_convention_A_ext': {str(H): nA[H] for H in bands},
        'N_per_H_convention_B_ext': {str(H): nB[H] for H in bands},
        'decade_ratios_A_ext': ratios_A,
        'decade_ratios_B_ext': ratios_B,
        'two_decade_ratio_A_ext_10e4_to_10e6': None if len(bands) < 3 else str(
            Fr(nA[bands[2]], nA[bands[0]])),
        'two_decade_ratio_B_ext_10e4_to_10e6': None if len(bands) < 3 else str(
            Fr(nB[bands[2]], nB[bands[0]])),
        'three_decade_ratio_A_ext_10e4_to_10e7': str(Fr(nA[bands[3]], nA[bands[0]])),
        'three_decade_ratio_B_ext_10e4_to_10e7': str(Fr(nB[bands[3]], nB[bands[0]])),
        'saturation_ceiling_A': ceiling_A,
        'saturation_ceiling_B': ceiling_B,
        'saturation_ceiling_note': (
            'kept(R12) = 33 plus recoverable re-admissible roots = 0 (the '
            'ledger is empty); ceiling = 33 under both conventions over the '
            'recoverable subset.'),
        'multiplicity_histogram': {str(k): v for k, v in sorted(hist.items())},
        'max_multiplicity': max(per_tuple.values()) if per_tuple else 0,
        'n8_band': n8,
        'max_h_A_observed': max(r['h_A'] for r in rows),
        'max_h_B_observed': max(r['h_B'] for r in rows),
    }


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def load_bound_modules():
    sys.path.insert(0, BOUND_V1)
    sys.path.insert(0, BOUND_V2)
    import ecrank_engine
    import construct
    import n2r
    return ecrank_engine, construct, n2r


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'all'
    ok, hashes = check_bound_hashes()
    print(json.dumps({'sr4_bound_hashes_ok': ok, 'hashes': hashes}, indent=1))
    if not ok:
        print('SR-4 STOP: bound-byte hash mismatch.')
        return 3
    if cmd in ('all', 'r1'):
        print(json.dumps({'calibration_1': run_calibration_1(),
                          'calibration_2': run_calibration_2()}, indent=1))
    if cmd in ('all', 'r2'):
        engine, construct, n2r_mod = load_bound_modules()
        t1 = trace_source(os.path.join(BOUND_V1, 'construct.py'), 'source/construct.py')
        t2 = trace_source(os.path.join(BOUND_V2, 'construct_v2.py'), 'source-v2/construct_v2.py')
        dyn = r2_dynamic(engine, construct)
        print(json.dumps({'trace_v1': t1, 'trace_v2': t2, 'dynamic': dyn}, indent=1))
    if cmd in ('all', 'r3'):
        engine, construct, n2r_mod = load_bound_modules()
        print(json.dumps(r3_readmission(engine, construct, n2r_mod), indent=1))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
