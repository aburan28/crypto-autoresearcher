"""Falsification probes, each shipped with the null object that makes its
output readable.

House rule, from docs/inventor-protocol.md ("controls before belief") and from
KN-FIND-001 ("a negative harness reported first"): a probe that has not been
shown to (a) fire on an object where the claim is false by construction and
(b) stay silent on an object where the claim is true by construction, reports
nothing at all.  Every probe below returns its control outcomes alongside its
measurement, and the driver refuses to report a measurement whose controls
failed.
"""

import random
from collections import Counter

from . import ec, fp


# ===========================================================================
# KN-FIND-a1f3c2 : Semaev monodromy is C_2^{m-2} for EVERY prime-field curve
# ===========================================================================
#
# C_2^{m-2} acting simply transitively on 2^{m-2} sheets is a REGULAR (Galois)
# cover.  Over a Galois cover every unramified specialisation factors into
# irreducible factors of EQUAL degree, that degree being the order of the
# Frobenius element.  Every non-identity element of C_2^{m-2} has order 2.
#
# Admissible shapes are therefore exactly [1]*2^(m-2) and [2]*2^(m-3).
# One observation of [1,3], [3,5], [8] or [1,1,2] refutes the claim.

def admissible_shapes(m):
    n = 2 ** (m - 2)
    return {tuple([1] * n), tuple([2] * (n // 2))}


def null_c2_power(ds, p):
    """Null object: minimal polynomial of  ±s_1 ±s_2 ... ±s_k,  s_i^2 = d_i.

    Its splitting field is a compositum of at most k quadratic extensions, so
    its Galois group embeds in C_2^k and has exponent 2 -- the same group the
    claim asserts for the Semaev cover.  Built by iterated resultant, so the
    s_i never have to exist in F_p.  A correct pipeline reports ONLY admissible
    shapes here; anything else means the pipeline itself manufactures
    violations and no Semaev measurement may be believed.
    """
    g = fp.norm([-ds[0], 0, 1], p)
    for d in ds[1:]:
        target = 2 * fp.deg(g)
        xs = list(range(target + 1))
        ys = [fp.resultant(g, fp.norm([X * X - d, -2 * X, 1], p), p) for X in xs]
        g = fp.interpolate(xs, ys, p)
    return g


def probe_monodromy(m, primes, trials, seed):
    """Search for a Semaev specialisation whose shape refutes C_2^{m-2}."""
    rng = random.Random(seed)
    adm = admissible_shapes(m)
    target_deg = 2 ** (m - 2)

    # ---- control A: null object with exponent-2 Galois group ---------------
    null_shapes, null_viol, null_n = Counter(), 0, 0
    for p in primes:
        for _ in range(trials):
            ds = [rng.randrange(1, p) for _ in range(m - 2)]
            f = null_c2_power(ds, p)
            if fp.deg(f) != target_deg or not fp.is_squarefree(f, p):
                continue
            s = tuple(fp.factor_pattern(f, p))
            null_shapes[s] += 1
            null_n += 1
            if s not in adm:
                null_viol += 1

    # ---- control B: positive, the polynomial really is the summation ideal --
    pos_ok = pos_fail = 0
    for p in primes:
        for _ in range(max(2, trials // 6)):
            a, b = rng.randrange(p), rng.randrange(p)
            if not ec.nonsingular(a, b, p):
                continue
            pts = ec.affine_points(a, b, p)
            if len(pts) < m:
                continue
            chosen = [rng.choice(pts) for _ in range(m - 1)]
            S = None
            for q in chosen:
                S = ec.add_points(S, q, a, p)
            if S is None:
                continue
            last = ec.negate(S, p)
            xs = [q[0] for q in chosen] + [last[0]]
            v = ec.S4(*xs, a, b, p) if m == 4 else ec.S5(*xs, a, b, p)
            if v is None:
                continue
            pos_ok, pos_fail = (pos_ok + 1, pos_fail) if v == 0 else (pos_ok, pos_fail + 1)

    # ---- measurement -------------------------------------------------------
    shapes, witnesses = Counter(), []
    used = skipped = 0
    for p in primes:
        for _ in range(trials):
            a, b = rng.randrange(p), rng.randrange(p)
            if not ec.nonsingular(a, b, p):
                continue
            others = [rng.randrange(p) for _ in range(m - 1)]
            f = ec.summation_fibre(m, others, a, b, p)
            if f is None or fp.deg(f) != target_deg or not fp.is_squarefree(f, p):
                skipped += 1
                continue
            s = tuple(fp.factor_pattern(f, p))
            shapes[s] += 1
            used += 1
            if s not in adm and len(witnesses) < 20:
                witnesses.append({'p': p, 'a': a, 'b': b,
                                  'others': others, 'shape': list(s),
                                  'poly': f})

    viol = sum(c for s, c in shapes.items() if s not in adm)
    return {
        'm': m,
        'controls': {
            'null_object_violations': null_viol,
            'null_object_tested': null_n,
            'null_object_shapes': {str(list(k)): v for k, v in null_shapes.items()},
            'positive_control_vanish': pos_ok,
            'positive_control_fail': pos_fail,
            'controls_passed': null_viol == 0 and pos_fail == 0 and null_n > 0 and pos_ok > 0,
        },
        'specialisations_used': used,
        'specialisations_skipped': skipped,
        'shapes': {str(list(k)): v for k, v in sorted(shapes.items(), key=lambda kv: -kv[1])},
        'violations': viol,
        'violation_rate': (viol / used) if used else None,
        'witnesses': witnesses,
        'verdict': ('claim_survives' if used and viol == 0 else
                    'claim_refuted' if used else 'no_data'),
    }


# ===========================================================================
# KN-FIND-c7d31e : BKK Speedup Theorem
# ===========================================================================
#
# The finding proves  gamma_m = Pr[>= m-1 of m indices in the first half]
#                            = (m+1)/2^m
# and then reports an empirical table exceeding that value in every row,
# attributing the gap to "EC group law gives ~0.1 bonus in gamma above the
# theoretical floor".
#
# Rival explanation tested here: the table reports per-TARGET success
# (at least one of a target's decompositions is BKK-visible), not the
# per-DECOMPOSITION retention the theorem predicts.  These differ by the
# decomposition multiplicity and need no elliptic curve at all.

REPORTED_TABLE = {2: 0.86, 3: 0.66, 4: 0.35, 5: 0.27}


def gamma_theory(m):
    return (m + 1) / 2 ** m


def visible(combo, half):
    """BKK sparse check: sweep (m-1)-tuples from the first half of the factor
    base and look the remaining point up in the full base.  A decomposition is
    found iff at least m-1 of its m indices lie in the first half."""
    return sum(1 for i in combo if i < half) >= len(combo) - 1


def probe_bkk_iid(m, B, trials, seed):
    """The theorem's own model: i.i.d. Uniform{1..B}, a single decomposition."""
    rng = random.Random(seed)
    half = B // 2
    hit = sum(1 for _ in range(trials)
              if visible([rng.randrange(B) for _ in range(m)], half))
    return hit / trials


def probe_bkk_null_multiplicity(m, B, k, trials, seed):
    """NULL OBJECT: a target carrying k i.i.d. decompositions, no curve anywhere.

    If this reproduces the reported excess, the excess cannot be evidence of an
    elliptic-curve group-law effect.
    """
    rng = random.Random(seed)
    half, hit = B // 2, 0
    for _ in range(trials):
        for _ in range(k):
            if visible([rng.randrange(B) for _ in range(m)], half):
                hit += 1
                break
    return hit / trials


def decompositions(F, m, a, p):
    """target -> list of index multisets i_1 <= ... <= i_m summing to it."""
    cur = {}
    for i, P in enumerate(F):
        cur.setdefault(P, []).append((i,))
    for _ in range(m - 1):
        nxt = {}
        for S, combos in cur.items():
            for i, P in enumerate(F):
                tail = [c for c in combos if c[-1] <= i]
                if not tail:
                    continue
                T = ec.add_points(S, P, a, p)
                bucket = nxt.setdefault(T, [])
                for c in tail:
                    bucket.append(c + (i,))
        cur = nxt
    return cur


def probe_bkk_curve(m, a, b, p, B):
    """Real curve, the two estimands separated."""
    pts = sorted(ec.affine_points(a, b, p))
    F = pts[:B]
    half = B // 2
    dec = decompositions(F, m, a, p)
    ndec = nvis = ntar = ntar_vis = 0
    mult = 0
    for T, combos in dec.items():
        if T is None:
            continue
        ntar += 1
        mult += len(combos)
        seen = False
        for c in combos:
            ndec += 1
            if visible(c, half):
                nvis += 1
                seen = True
        if seen:
            ntar_vis += 1
    return {
        'm': m, 'p': p, 'a': a, 'b': b, 'B': B,
        'group_order': len(pts) + 1,
        'per_decomposition': (nvis / ndec) if ndec else None,
        'per_target': (ntar_vis / ntar) if ntar else None,
        'mean_multiplicity': (mult / ntar) if ntar else None,
        'n_targets': ntar, 'n_decompositions': ndec,
        'theory': gamma_theory(m),
        'per_decomposition_error': (abs(nvis / ndec - gamma_theory(m)) if ndec else None),
    }
