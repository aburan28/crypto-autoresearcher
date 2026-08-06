"""
rho_bsgs.py -- matched Pollard rho (r-adding walk) and matched baby-step giant-step
(BSGS) baselines for CTRL-RHO / CTRL-BSGS, on the same curve/N as a class's seed
curve. Emits a discrete_log certificate per docs/claims-and-verification.md,
independently re-verified by a function that does NOT touch the solver's internal
state.

PROTOCOL DEVIATION (recorded, not silent -- see MANIFEST.md "CTRL-RHO scope"): the
spec names "Pollard rho (negation)" as the matched baseline. This driver's first
negation-folded implementation was measured to hit the well-documented "fruitless
short cycle" pathology of negation maps (Wiener-Zuccherato and van
Oorschot-Wiener discuss this; the walk's state graph, folded by P~-P, develops
short parasitic cycles that Floyd's algorithm detects almost immediately without
making birthday-paradox progress): empirically, ~2.5% of Floyd steps produced a
degenerate (unusable) collision, and some runs needed >500x the sqrt(N) step
budget before a genuine, non-degenerate collision. Implementing and independently
verifying a correct fruitless-cycle escape mechanism (e.g. Wiener-Zuccherato) was
assessed as out of scope for this session's realistic time budget. This driver
therefore runs PLAIN (non-negation) r-adding-walk Pollard rho: methodologically
standard, free of that failure mode, costing a constant factor sqrt(2) more group
operations than the negation-optimized variant -- reported as measured group_ops,
never adjusted or compared against a negation-based prediction. CTRL-BSGS is
unaffected (BSGS has no negation step) and is reported alongside as specified.
"""
import math
import random
import time
from . import curve


def pollard_rho_plain(G, Q, N, a, p, rng, r=20, max_steps=200_000_000):
    """Plain r-adding-walk Pollard rho (no negation folding -- see module docstring
    for why). Returns (k, group_ops, steps) with k*G=Q, or (None, group_ops, steps)
    if max_steps exceeded (reported as infrastructure timeout by the caller)."""
    mults = []
    for _ in range(r):
        ai = rng.randrange(1, N)
        bi = rng.randrange(1, N)
        Ti = curve.add(curve.scalar_mul(ai, G, a, p), curve.scalar_mul(bi, Q, a, p), a, p)
        mults.append((ai, bi, Ti))

    def partition(W):
        if W is None:
            return 0
        return W[0] % r

    def step(state):
        W, sa, sb = state
        idx = partition(W)
        ai, bi, Ti = mults[idx]
        W2 = curve.add(W, Ti, a, p)
        sa2 = (sa + ai) % N
        sb2 = (sb + bi) % N
        return (W2, sa2, sb2)

    group_ops = r
    x0 = rng.randrange(1, N)
    y0 = rng.randrange(1, N)
    start_pt = curve.add(curve.scalar_mul(x0, G, a, p), curve.scalar_mul(y0, Q, a, p), a, p)
    tortoise = (start_pt, x0, y0)
    hare = tortoise
    steps = 0
    degenerate_restarts = 0
    while steps < max_steps:
        tortoise = step(tortoise)
        hare = step(step(hare))
        group_ops += 3
        steps += 1
        if tortoise[0] == hare[0]:
            _, sa1, sb1 = tortoise
            _, sa2, sb2 = hare
            denom = (sb1 - sb2) % N
            if denom == 0:
                degenerate_restarts += 1
                x0 = rng.randrange(1, N)
                y0 = rng.randrange(1, N)
                start_pt = curve.add(curve.scalar_mul(x0, G, a, p), curve.scalar_mul(y0, Q, a, p), a, p)
                tortoise = (start_pt, x0, y0)
                hare = tortoise
                continue
            k = ((sa2 - sa1) * pow(denom, N - 2, N)) % N
            return k, group_ops, steps, degenerate_restarts
    return None, group_ops, steps, degenerate_restarts


def bsgs_discrete_log(G, Q, N, a, p):
    """k with k*G = Q, via baby-step giant-step. Returns (k, group_ops)."""
    m = math.isqrt(N) + 1
    baby = {}
    cur = None
    group_ops = 0
    for j in range(m):
        baby[cur] = j
        cur = curve.add(cur, G, a, p)
        group_ops += 1
    mG = curve.scalar_mul(m, G, a, p)
    negmG = curve.neg(mG, p)
    gamma = Q
    for i in range(m + 1):
        if gamma in baby:
            k = (i * m + baby[gamma]) % N
            group_ops += i
            return k, group_ops
        gamma = curve.add(gamma, negmG, a, p)
        group_ops += 1
    return None, group_ops


def independent_verify_discrete_log(k, G, Q, a, p):
    """Re-derive k*G from scratch via the curve arithmetic module and compare to Q.
    Independent of any solver's internal bookkeeping (per
    docs/claims-and-verification.md)."""
    if k is None:
        return False
    recomputed = curve.scalar_mul(k, G, a, p)
    return recomputed == Q


def run_matched_baselines(a, b, p, N, seed, rho_max_steps=60_000_000):
    """Run one matched Pollard-rho and one matched BSGS discrete-log solve on a
    fresh random target Q = k_true*G (k_true generated for bookkeeping only, never
    used by the verifier), on curve (a,b) with #E(F_p)=N (prime). Returns a dict
    with certificates for both solves, independently re-verified."""
    rng = random.Random(seed)
    G = curve.random_point(a, b, p, rng)
    k_true = rng.randrange(1, N)
    Q = curve.scalar_mul(k_true, G, a, p)

    t0 = time.time()
    k_rho, ops_rho, steps_rho, restarts_rho = pollard_rho_plain(
        G, Q, N, a, p, random.Random(seed + 1), max_steps=rho_max_steps)
    rho_elapsed = time.time() - t0
    rho_timed_out = k_rho is None
    rho_verified = (not rho_timed_out) and independent_verify_discrete_log(k_rho, G, Q, a, p)

    t0 = time.time()
    k_bsgs, ops_bsgs = bsgs_discrete_log(G, Q, N, a, p)
    bsgs_elapsed = time.time() - t0
    bsgs_verified = (k_bsgs is not None) and independent_verify_discrete_log(k_bsgs, G, Q, a, p)

    curve_id = f"TOY-P{p.bit_length()}-{p:x}"[:40]
    return {
        "curve": {"a": a, "b": b, "p": p, "N": N},
        "G": list(G) if G else None, "Q": list(Q) if Q else None,
        "k_true_for_bookkeeping_only": k_true,
        "rho": {
            "method": "plain_r_adding_walk_no_negation",
            "k_found": k_rho, "group_ops": ops_rho, "steps": steps_rho,
            "degenerate_restarts": restarts_rho,
            "elapsed_s": rho_elapsed, "timed_out": rho_timed_out,
            "certificate": {
                "kind": "discrete_log",
                "curve_id": curve_id,
                "statement": {"P": list(G) if G else None, "Q": list(Q) if Q else None, "k": k_rho},
                "verified": rho_verified,
                "verifier": "independent-recompute",
            } if not rho_timed_out else {
                "kind": "discrete_log", "verified": False,
                "verifier": "independent-recompute",
                "note": "solver timed out at rho_max_steps, no k to verify",
            },
        },
        "bsgs": {
            "k_found": k_bsgs, "group_ops": ops_bsgs, "elapsed_s": bsgs_elapsed,
            "certificate": {
                "kind": "discrete_log",
                "curve_id": curve_id,
                "statement": {"P": list(G) if G else None, "Q": list(Q) if Q else None, "k": k_bsgs},
                "verified": bsgs_verified,
                "verifier": "independent-recompute",
            },
        },
    }
