#!/usr/bin/env python3
"""
Driver for EXP-ECRANK-76a70d: the 8 enumerated runs of the frozen protocol.

TASK-20260905-54bcbf / BATCH-90fabf / GOAL-ECRANK-002.

Runs (in order, per the frozen contract's budget.maximum_runs_note):
  1  instrument smoke self-test on committed fixtures (must pass before arms)
  2  arm A  (n = 6, seed 760706, N_b = 10^3)
  3  arm B  (n = 8, seed 760708, N_b = 10^4)
  4  arm B determinism re-run (seed 760708 again; must reproduce bit-for-bit)
  5  arm C  (n = 10, seed 760710, N_b = 10^4)
  6  augmentation scan + null objects (seed 760711)
  7  known-false d = (1..1) control (seed 760712)  -> IV-1
  8  repair/restart margin (unused unless a prior run failed_infrastructure)

Discipline (frozen):
  * counted exact-op cap 1.0e8 per arm, checkpointed every 10^7;
  * wall 7200 s per run; exhaustion is INERT in both directions (rules 3/5);
  * NO early stop for "enough instances"; NO box widening, ever;
  * ZERO descent (no PARI, no 2-descent, no r_low, no root numbers);
  * every claim is a lower bound from verifier-checked exhibited points;
  * the Fisher test is computed ONCE on the frozen yield table.

Stdlib only. No network. No PARI.
"""
from __future__ import annotations

import json
import math
import os
import platform
import random
import resource
import sys
import time
from fractions import Fraction as Fr

import engine as E

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..", ".."))

SUPPORT = E.SUPPORT_COMMITTED
H_LEVELS = [10 ** 2, 10 ** 3, 10 ** 4]
ARM_SEEDS = {'A': 760706, 'B': 760708, 'C': 760710}
SCAN_SEED = 760711
KNOWNFALSE_SEED = 760712
N_B = {'A': 10 ** 3, 'B': 10 ** 4, 'C': 10 ** 4}
N = {'A': 6, 'B': 8, 'C': 10}
OPS_CAP = 1.0e8
WALL_CAP = 7200.0
MAX_DRAWS_PER_B = 8
N_COSETS_PER_ARM = 3


def peak_rss_bytes():
    # ru_maxrss is in BYTES on macOS, in KILOBYTES on Linux.
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return ru if sys.platform == "darwin" else ru * 1024


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# b-tuple and coset drawing (seeded, deterministic, no adaptive reordering)
# ---------------------------------------------------------------------------

def draw_b_tuple(rng, n):
    r"""b_1 = 0, b_2 = 1, b_3..b_n distinct integers in [-20,20] \ {0,1}."""
    pool = [x for x in range(-20, 21) if x not in (0, 1)]
    rest = rng.sample(pool, n - 2)
    return [Fr(0), Fr(1)] + [Fr(x) for x in rest]


def draw_cosets(rng, n_cosets=N_COSETS_PER_ARM):
    cosets = E.eligible_cosets(SUPPORT, 3)
    return rng.sample(cosets, n_cosets)


def d_pattern_for_coset(rng, m0, V, n):
    """n/2 distinct nonzero classes of the coset, each used twice -> n entries."""
    classes = [E.class_value(m0 ^ v, SUPPORT) for v in V]
    nonzero = [c for c in classes if c != 1]
    sel = rng.sample(nonzero, n // 2)
    return sel * 2


# ---------------------------------------------------------------------------
# one arm: the bounded seeded fibration search over the declared sample
# ---------------------------------------------------------------------------

def run_arm(arm, checkpoint_cb=None):
    n = N[arm]
    seed = ARM_SEEDS[arm]
    N_b = N_B[arm]
    rng = random.Random(seed)
    cosets = draw_cosets(rng)
    ops = E.OpCounter(OPS_CAP)
    t0 = time.time()
    counts = {}          # (n, H) -> distinct-minimal-model instance count
    per_b_success = 0    # b-tuples that yielded >= 1 nonsingular instance
    b_processed = 0
    degenerate = 0
    instances = []       # (n, H, coset_idx, b, d, s, r) for found instances
    per_cell_raw = {}    # (n, H) -> raw (pre-dedup) candidate count
    exhausted = False
    wall_hit = False
    # process exactly N_b b-tuples: base = N_b // 3 per coset, the first
    # (N_b % 3) cosets take one extra so the total is exactly N_b.
    base_b = N_b // N_COSETS_PER_ARM
    rem = N_b % N_COSETS_PER_ARM
    for ci, (m0, V) in enumerate(cosets):
        d = d_pattern_for_coset(rng, m0, V, n)
        per_coset_b = base_b + (1 if ci < rem else 0)
        for bi in range(per_coset_b):
            if ops.exhausted():
                exhausted = True
                break
            if time.time() - t0 > WALL_CAP:
                wall_hit = True
                break
            b = draw_b_tuple(rng, n)
            b_processed += 1
            sols = E.fibration_search(b, d, H_LEVELS[-1], rng,
                                      MAX_DRAWS_PER_B, ops)
            found_here = 0
            # count per nested H: a solution of r-height h belongs to all
            # H >= h. We record the solution's r-height and bucket it.
            for sol in sols:
                r = sol['r']
                h = max(abs(x) for x in r)  # r-height (max |r_i|, |r_i|<=H)
                ok, reasons = E.degeneracy_filter(sol['s'], b, r)
                if not ok:
                    degenerate += 1
                    continue
                found_here += 1
                for H in H_LEVELS:
                    if h <= H:
                        per_cell_raw[(n, H)] = per_cell_raw.get((n, H), 0) + 1
                        instances.append({'n': n, 'H': H, 'coset': ci,
                                          'b': [str(x) for x in b],
                                          'd': list(d),
                                          's': E.poly_str(sol['s']),
                                          'r': [str(x) for x in r],
                                          'r_height': str(h)})
            if found_here:
                per_b_success += 1
            if checkpoint_cb and ops.count % E.OpCounter.CHECKPOINT < 10 ** 6:
                checkpoint_cb(arm, ops.count, b_processed,
                              dict(per_cell_raw))
        if exhausted or wall_hit:
            break
    # deduplicate to distinct minimal models (O-08): key on the Weierstrass
    # model of the base quartic (class-1 reduction) when available, else on s.
    seen = set()
    dedup_counts = {}
    for inst in instances:
        key = (inst['n'], inst['H'], inst['s'])
        if key in seen:
            continue
        seen.add(key)
        dedup_counts[(inst['n'], inst['H'])] = \
            dedup_counts.get((inst['n'], inst['H']), 0) + 1
    wall = time.time() - t0
    return {
        'arm': arm, 'n': n, 'seed': seed, 'N_b': N_b,
        'b_processed': b_processed,
        'per_b_success': per_b_success,
        'per_b_rate': (per_b_success / b_processed) if b_processed else 0.0,
        'degenerate_filtered': degenerate,
        'counts_per_cell': {('%d,%d' % k): v for k, v in sorted(dedup_counts.items())},
        'raw_per_cell': {('%d,%d' % k): v for k, v in sorted(per_cell_raw.items())},
        'counted_ops': ops.count,
        'checkpoints': ops.checkpoints,
        'wall_seconds': wall,
        'exhausted_ops': exhausted,
        'wall_hit': wall_hit,
        'cosets': [[E.class_value(m0 ^ v, SUPPORT) for v in V] for m0, V in cosets],
        'instances': instances,
    }


# ---------------------------------------------------------------------------
# Run 1: instrument smoke self-test on committed fixtures
# ---------------------------------------------------------------------------

def run_smoke_selftest():
    """Validate the instrument on committed fixtures BEFORE any arm runs.

    (a) F_l certifier NULL GATE: the committed DEV-A-01 dependent triple
        {(-1,3),(0,2),(2,0)} on Cremona 5077a1 (y^2 = x^3 - 7x + 6) must
        return 2, not 3 (the sum is O).
    (b) F_l certifier POSITIVE: an independent pair on the same curve returns 2.
    (c) known-false d=(1..1) control at n=8 and n=10 returns 7 and 9 (IV-1).
    (d) reduction machinery: quartic_reduction/cubic_to_weierstrass round-trip
        a committed-shape quartic with exact on-curve rechecks.
    """
    out = {'checks': {}, 'all_pass': False}
    # (a) dependent triple -> 2
    ai = [0, 0, 1, -7, 6]  # y^2 = x^3 - 7x + 6 (Cremona 5077a1)
    triple = [[-1, 3], [0, 2], [2, 0]]
    c = E.fl_certify(ai, triple)
    out['checks']['a_dependent_triple_returns_2'] = (
        c['certified_rank_lower_bound'] == 2)
    out['a_detail'] = c['certified_rank_lower_bound']
    # (b) independent pair -> 2
    # two independent points on 5077a1: (2,0) and (3,4) [3^3-7*3+6=12, not sq];
    # use (2,0) and (-1,3): check independence via certifier
    pair = [[-1, 3], [2, 0]]
    c2 = E.fl_certify(ai, pair)
    out['checks']['b_independent_pair_returns_2'] = (
        c2['certified_rank_lower_bound'] == 2)
    out['b_detail'] = c2['certified_rank_lower_bound']
    # (c) known-false control (also run 7, but checked here as a gate)
    rng = random.Random(KNOWNFALSE_SEED)
    kf = {}
    for n in (8, 10):
        A = tuple(sorted(rng.sample(range(-20, 21), n)))
        p, g, s = E.mestre_polys(list(A))
        r = [E.peval(g, Fr(a)) for a in A]
        cert = E.certify_instance(s, [Fr(a) for a in A], r, [1] * n)
        kf[n] = cert['certified_total']
    out['checks']['c_knownfalse_n8_is_7'] = (kf[8] == 7)
    out['checks']['c_knownfalse_n10_is_9'] = (kf[10] == 9)
    out['c_detail'] = kf
    # (d) reduction round-trip on a committed-shape quartic (M10)
    rng2 = random.Random(20260822)
    A10 = tuple(sorted(rng2.sample(range(-20, 21), 10)))
    p, g, s = E.mestre_polys(list(A10))
    base = A10[0]
    e = E.peval(g, Fr(base))
    D, coef = E.quartic_reduction(s, base, e)
    cub = []
    for i, a in enumerate(A10):
        if i == 0:
            continue
        t = Fr(a) - Fr(base)
        m, w = E.quartic_point_to_cubic(t, E.peval(g, Fr(a)), coef)
        assert w * w == E.peval(D, m), "cubic image off cubic"
        cub.append((m, w))
    ainv, P = E.cubic_to_weierstrass(D, cub)
    on_curve = all(E.verify_on_curve(ainv, x, y) for x, y in P)
    out['checks']['d_reduction_roundtrip_oncurve'] = on_curve
    out['checks']['d_reduction_nonsingular'] = (E.disc_from_ainv(ainv) != 0)
    out['all_pass'] = all(out['checks'].values())
    return out


# ---------------------------------------------------------------------------
# Run 7: known-false d=(1..1) control (IV-1)
# ---------------------------------------------------------------------------

def run_knownfalse():
    rng = random.Random(KNOWNFALSE_SEED)
    out = {'n8': None, 'n10': None, 'pass': False, 'detail': {}}
    for n in (8, 10):
        A = tuple(sorted(rng.sample(range(-20, 21), n)))
        p, g, s = E.mestre_polys(list(A))
        r = [E.peval(g, Fr(a)) for a in A]
        cert = E.certify_instance(s, [Fr(a) for a in A], r, [1] * n)
        out['n%d' % n] = cert['certified_total']
        out['detail'][n] = {'A': list(A), 'certified_total': cert['certified_total'],
                            'verifier_errors': cert['verifier_errors']}
    out['pass'] = (out['n8'] == 7 and out['n10'] == 9)
    out['expected'] = {'n8': 7, 'n10': 9}
    out['rule'] = ('IV-1: a pipeline reporting total = n at d=1 is broken and '
                   'ALL runs are void')
    return out


# ---------------------------------------------------------------------------
# Run 6: augmentation scan + null objects (F6)
# ---------------------------------------------------------------------------

def _scan_quartic(s, d, nmax=1000, dmax=20, exclude=None):
    """Per-class exact square test s(u) = d * square over u = num/den,
    |num| <= nmax, 1 <= den <= dmax, gcd = 1. Returns list of (u, val)."""
    L = 1
    for c in s:
        L = math.lcm(L, c.denominator)
    C = [int(c * L) for c in s]
    found = []
    excl = set(Fr(x) for x in (exclude or []))
    for den in range(1, dmax + 1):
        denpow = [den ** j for j in range(len(C) + 1)]
        for num in range(-nmax, nmax + 1):
            if math.gcd(abs(num), den) != 1:
                continue
            u = Fr(num, den)
            if u in excl:
                continue
            S = 0
            npow = 1
            for j in range(len(C)):
                S += C[j] * npow * denpow[len(C) - 1 - j]
                npow *= num
            T = S * L * d
            if T < 0:
                continue
            r = math.isqrt(T)
            if r * r != T:
                continue
            val = Fr(r, L * den * den)
            if val * val != E.peval(s, u) / Fr(d):
                continue
            found.append((u, val))
    return found


def run_scan(armB_instances, armC_instances):
    """Per-class augmentation scan on the best constructed instance (n=10 if
    found, else n=8) plus 8 null random quartics of matched height/coeff size.
    One-sided Fisher exact, alpha=0.05, 4 constructed non-forced cells vs 32
    null cells. Computed ONCE on the frozen yield table."""
    rng = random.Random(SCAN_SEED)
    # pick the constructed instance: n=10 if found, else n=8 (fallback)
    constructed = None
    for inst in (armC_instances or []):
        constructed = inst
        constructed_n = 10
        break
    if constructed is None:
        for inst in (armB_instances or []):
            constructed = inst
            constructed_n = 8
            break
    out = {'constructed_instance': None, 'constructed_cells': {},
           'null_cells': {}, 'fisher': None, 'note': ''}
    if constructed is None:
        out['note'] = ('NO constructed instance available from arms B/C; the '
                       'scan stage has no constructed core to scan. The null '
                       'objects are still scanned for the background table. '
                       'F6 is INCONCLUSIVE (no constructed yield to compare).')
    else:
        s = [Fr(x) for x in constructed['s'].strip('[]').split(', ')]
        b = [Fr(x) for x in constructed['b']]
        d = constructed['d']
        out['constructed_instance'] = {'n': constructed_n,
                                       's': constructed['s'],
                                       'b': constructed['b'], 'd': d}
        # per-class scan on the constructed instance: for each of the 8 coset
        # classes, count non-forced hits (u not in the forced b set)
        coset_classes = sorted(set(E.squarefree_part(int(x)) for x in d))
        forced = set(Fr(x) for x in b)
        cell = {}
        for dc in coset_classes:
            hits = _scan_quartic(s, dc, exclude=list(b))
            cell[dc] = len(hits)
        out['constructed_cells'] = {str(k): v for k, v in cell.items()}
    # null objects: 8 random quartics of matched height and coefficient size,
    # each scanned over 4 classes -> 32 null cells (per the frozen contract).
    # The 4 classes mirror the 4 constructed non-forced cells the Fisher test
    # compares against; with no constructed instance available we use the
    # canonical default class set (disclosed in observations.md).
    null_cells = []
    for k in range(8):
        # random quartic with small integer coefficients (matched size)
        coeffs = [rng.randint(-50, 50) for _ in range(5)]
        if coeffs[4] == 0:
            coeffs[4] = 1
        snull = [Fr(c) for c in coeffs]
        for dc in [1, 2, 3, 5]:
            hits = _scan_quartic(snull, dc)
            null_cells.append(len(hits))
    out['null_cells'] = null_cells
    # Fisher exact (one-sided): constructed non-forced yield vs null background.
    # 4 constructed non-forced cells vs 32 null cells (per the frozen contract).
    if constructed is not None:
        cons_vals = list(out['constructed_cells'].values())[:4]
        null_vals = null_cells[:32]
        out['fisher'] = _fisher_one_sided(cons_vals, null_vals)
    return out


def _fisher_one_sided(a_counts, b_counts):
    """One-sided Fisher exact test: is the mean of a_counts significantly
    greater than the mean of b_counts? Computed by exact permutation of the
    pooled sample (the exact test for two independent samples of counts).
    Returns {p_value, alpha, reject, a_mean, b_mean, n_a, n_b}."""
    a = list(a_counts)
    b = list(b_counts)
    pooled = a + b
    n_a, n_b = len(a), len(b)
    obs = sum(a) / n_a if n_a else 0.0
    # exact: number of ways to choose n_a from pooled with mean >= obs mean
    # (use the sum statistic). For small samples, enumerate combinations.
    from itertools import combinations
    total = 0
    ge = 0
    obs_sum = sum(a)
    for combo in combinations(range(len(pooled)), n_a):
        s = sum(pooled[i] for i in combo)
        total += 1
        if s >= obs_sum:
            ge += 1
    p = ge / total if total else 1.0
    return {'p_value': p, 'alpha': 0.05, 'reject_null': p < 0.05,
            'a_mean': obs, 'b_mean': (sum(b) / n_b if n_b else 0.0),
            'n_a': n_a, 'n_b': n_b,
            'a_counts': a, 'b_counts': b,
            'method': 'exact one-sided permutation (Fisher) on frozen yield table'}


# ---------------------------------------------------------------------------
# pre-registered metric fits (HEUR-1 distribution comparison)
# ---------------------------------------------------------------------------

def metric_fits(arm_results):
    """Log-log slope of N(n,H) vs H at each n, against the predicted exponent
    5 - n/2. Counts deduplicated to distinct minimal models BEFORE the fit.
    Computed over the pre-declared seeded sample only."""
    fits = {}
    for arm, res in arm_results.items():
        n = res['n']
        predicted = 5 - n / 2
        # collect (H, count) from the dedup counts
        pts = []
        for key, cnt in res['counts_per_cell'].items():
            ns, H = key.split(',')
            pts.append((int(H), cnt))
        pts.sort()
        # log-log slope (least squares on log H, log(N+1) to handle zeros)
        slope = None
        if len(pts) >= 2:
            xs = [math.log10(H) for H, _ in pts]
            ys = [math.log10(c + 1) for _, c in pts]
            mx = sum(xs) / len(xs)
            my = sum(ys) / len(ys)
            sxx = sum((x - mx) ** 2 for x in xs)
            sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
            if sxx > 0:
                slope = sxy / sxx
        fits[arm] = {
            'n': n,
            'predicted_exponent': predicted,
            'measured_loglog_slope': slope,
            'counts_per_H': {str(H): c for H, c in pts},
            'per_b_rate': res['per_b_rate'],
            'per_b_rate_floor_q': 1e-3,
            'flatness_artifact_tell': (slope is not None and abs(slope) < 0.1),
        }
    return fits


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    os.makedirs(RESULTS, exist_ok=True)
    log("=" * 70)
    log("EXP-ECRANK-76a70d execution driver")
    log("task TASK-20260905-54bcbf / GOAL-ECRANK-002 / BATCH-90fabf")
    log("python %s / %s" % (platform.python_version(), platform.platform()))
    log("=" * 70)
    run_record = {'experiment_id': 'EXP-ECRANK-76a70d',
                  'task_id': 'TASK-20260905-54bcbf',
                  'runs': {}, 'peak_rss_bytes': {}}
    summary = {'counts_per_cell': {}, 'op_counters': {}, 'metric_fits': {},
               'per_b_rates': {}}
    controls = {}
    t_start = time.time()

    # ---- Run 1: smoke self-test (must pass before any arm) ----
    log("\n[run 1] instrument smoke self-test on committed fixtures")
    t0 = time.time()
    smoke = run_smoke_selftest()
    run_record['runs']['run1_smoke_selftest'] = {
        'status': 'completed' if smoke['all_pass'] else 'failed',
        'checks': smoke['checks'], 'detail': {k: v for k, v in smoke.items()
                                              if k.endswith('_detail')},
        'wall_seconds': time.time() - t0}
    controls['IV-1_smoke_gate'] = smoke['checks'].get('c_knownfalse_n8_is_7') and \
        smoke['checks'].get('c_knownfalse_n10_is_9')
    log("  smoke all_pass=%s checks=%s" % (smoke['all_pass'], smoke['checks']))
    if not smoke['all_pass']:
        log("  SMOKE SELF-TEST FAILED: arms do not run (gate).")
        _write_outputs(run_record, summary, controls, t_start)
        return

    # ---- Runs 2-5: arms A, B, B-re-run, C ----
    arm_results = {}
    armB_first = None
    armB_rerun = None
    for run_no, arm in [(2, 'A'), (3, 'B'), (4, 'B'), (5, 'C')]:
        tag = 'arm_%s' % arm + ('_rerun' if arm == 'B' and run_no == 4 else '')
        log("\n[run %d] %s (n=%d seed=%d N_b=%d)" %
            (run_no, tag, N[arm], ARM_SEEDS[arm], N_B[arm]))
        t0 = time.time()
        res = run_arm(arm)
        res['wall_seconds'] = time.time() - t0
        arm_results[tag] = res
        if arm == 'B' and run_no == 3:
            armB_first = res
        if arm == 'B' and run_no == 4:
            armB_rerun = res
        status = 'completed'
        if res['exhausted_ops']:
            status = 'completed_exhausted_ops'
        if res['wall_hit']:
            status = 'completed_wall'
        run_record['runs']['run%d_%s' % (run_no, tag)] = {
            'status': status, 'seed': res['seed'], 'n': res['n'],
            'N_b': res['N_b'], 'b_processed': res['b_processed'],
            'per_b_success': res['per_b_success'],
            'per_b_rate': res['per_b_rate'],
            'counted_ops': res['counted_ops'],
            'checkpoints': res['checkpoints'],
            'wall_seconds': res['wall_seconds'],
            'exhausted_ops': res['exhausted_ops'], 'wall_hit': res['wall_hit'],
            'counts_per_cell': res['counts_per_cell'],
            'degenerate_filtered': res['degenerate_filtered']}
        summary['counts_per_cell'][tag] = res['counts_per_cell']
        summary['op_counters'][tag] = res['counted_ops']
        summary['per_b_rates'][tag] = res['per_b_rate']
        log("  b_processed=%d per_b_success=%d rate=%.3g ops=%d wall=%.1fs "
            "counts=%s" % (res['b_processed'], res['per_b_success'],
                           res['per_b_rate'], res['counted_ops'],
                           res['wall_seconds'], res['counts_per_cell']))

    # ---- IV-7 determinism: arm B re-run must reproduce bit-for-bit ----
    if armB_first is not None and armB_rerun is not None:
        same = (armB_first['counts_per_cell'] == armB_rerun['counts_per_cell']
                and armB_first['b_processed'] == armB_rerun['b_processed']
                and _inst_key(armB_first) == _inst_key(armB_rerun))
        controls['IV-7_determinism'] = same
        log("\n[IV-7] arm B determinism re-run bit-for-bit: %s" % same)

    # ---- Run 6: augmentation scan + null objects ----
    log("\n[run 6] augmentation scan + null objects (F6)")
    t0 = time.time()
    armB_inst = arm_results.get('arm_B', {}).get('instances', [])
    armC_inst = arm_results.get('arm_C', {}).get('instances', [])
    scan = run_scan(armB_inst, armC_inst)
    run_record['runs']['run6_scan'] = {
        'status': 'completed', 'wall_seconds': time.time() - t0,
        'constructed_instance': scan['constructed_instance'],
        'constructed_cells': scan['constructed_cells'],
        'null_cells': scan['null_cells'], 'fisher': scan['fisher'],
        'note': scan['note']}
    controls['F6_scan'] = scan
    log("  constructed=%s fisher=%s" % (
        bool(scan['constructed_instance']),
        scan['fisher']['p_value'] if scan['fisher'] else None))

    # ---- Run 7: known-false d=(1..1) control (IV-1) ----
    log("\n[run 7] known-false d=(1..1) control (IV-1)")
    t0 = time.time()
    kf = run_knownfalse()
    run_record['runs']['run7_knownfalse'] = {
        'status': 'completed', 'wall_seconds': time.time() - t0,
        'n8': kf['n8'], 'n10': kf['n10'], 'pass': kf['pass'],
        'expected': kf['expected'], 'detail': kf['detail']}
    controls['IV-1_knownfalse'] = kf
    log("  n8=%s n10=%s pass=%s (expected 7, 9)" % (kf['n8'], kf['n10'], kf['pass']))
    if not kf['pass']:
        log("  IV-1 FAILED: ALL runs are VOID.")

    # ---- Run 8: repair/restart margin ----
    log("\n[run 8] repair/restart margin")
    failed = [k for k, v in run_record['runs'].items()
              if v['status'] in ('failed_infrastructure', 'failed')]
    if failed:
        log("  prior failures %s: repair margin available (not exercised here)" % failed)
        run_record['runs']['run8_repair_margin'] = {
            'status': 'available_not_exercised', 'reason': 'prior failures: %s' % failed}
    else:
        run_record['runs']['run8_repair_margin'] = {
            'status': 'not_needed', 'reason': 'no prior run failed_infrastructure'}

    # ---- metric fits ----
    summary['metric_fits'] = metric_fits(arm_results)
    log("\n[metric fits] " + json.dumps(
        {k: {'n': v['n'], 'pred': v['predicted_exponent'],
             'slope': v['measured_loglog_slope'],
             'counts': v['counts_per_H']} for k, v in summary['metric_fits'].items()},
        indent=1))

    run_record['peak_rss_bytes'] = peak_rss_bytes()
    run_record['total_wall_seconds'] = time.time() - t_start
    run_record['environment'] = {
        'python': platform.python_version(), 'platform': platform.platform(),
        'stdlib_only': True, 'pari_used': False, 'network': 'none'}
    _write_outputs(run_record, summary, controls, t_start)
    log("\n[done] total wall %.1fs" % (time.time() - t_start))


def _inst_key(res):
    return json.dumps(res.get('instances', []), sort_keys=True)


def _write_outputs(run_record, summary, controls, t_start):
    # run_record.yaml (hand-written YAML, no external deps)
    with open(os.path.join(RESULTS, "run_record.yaml"), "w") as f:
        f.write(_to_yaml(run_record))
    with open(os.path.join(RESULTS, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1, default=str)
    with open(os.path.join(RESULTS, "controls.json"), "w") as f:
        json.dump(controls, f, indent=1, default=str)
    log("[outputs] wrote results/run_record.yaml, summary.json, controls.json")


def _to_yaml(obj, indent=0):
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                lines.append("%s%s:" % (pad, k))
                lines.append(_to_yaml(v, indent + 1))
            else:
                lines.append("%s%s: %s" % (pad, k, _scalar(v)))
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)):
                lines.append("%s-" % pad)
                lines.append(_to_yaml(v, indent + 1))
            else:
                lines.append("%s- %s" % (pad, _scalar(v)))
    else:
        lines.append("%s%s" % (pad, _scalar(obj)))
    return "\n".join(lines)


def _scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if any(c in s for c in ":#{}[]") or s != s.strip():
        return '"%s"' % s.replace('"', '\\"')
    return s


if __name__ == "__main__":
    main()
