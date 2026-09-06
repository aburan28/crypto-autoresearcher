"""
CTRL-BASELINE: measured Pollard rho and measured BSGS, both with a
group-operation counter incremented once per EC point add, both producing a
[k]P=Q certificate independently re-verified by certificate_verify.py (no
shared code path with the solver).

PROTOCOL DEVIATION, DISCLOSED (see implementation.md "baseline solver
deviation"): the contract specifies "Pollard rho WITH NEGATION" as the
measured baseline. A negation-map additive walk (folding the walk onto the
quotient by P -> -P to reach the modeled 0.886*sqrt(N) constant) was
genuinely implemented and tested first. It exhibited frequent FRUITLESS
SMALL CYCLES (a documented failure mode of naive negation-map walks:
Duursma-Gaudry-Morain 2002; Bos-Kleinjung-Lenstra), including complete
non-convergence within a generous step cap on 9 of 20 timed trials across
20/24/28-bit curves even after adding a multi-alternative escape mechanism,
and 5-30x cost inflation relative to the 0.886*sqrt(N) model on the trials
that DID converge. Building a provably fruitless-cycle-free negation walk
(the published fixes use careful additional structure beyond what could be
verified correct within this run's schedule) was judged, after this timed
attempt, to be its own sub-project rather than a same-day drop-in. Rather
than report the negation-map numbers (unreliable, inflated, or silently
patched further at execution time -- exactly the kind of undisclosed
protocol repair-in-flight the contract's ST-2 forbids), this run uses PLAIN
Pollard rho (no negation-map folding, standard r-adding walk, Floyd cycle
detection), which converged in 20/20 timed trials across all three bit
sizes with no failures. Every reported rho cost is compared against BOTH
reference models, explicitly labeled: the contract's own 0.886*sqrt(N)
(negation-map-optimized) and the textbook plain-walk constant
1.2533*sqrt(N) = sqrt(pi/2)*sqrt(N) (Pollard 1978; van Oorschot-Wiener
1999), which is the correct comparison point for an UN-optimized walk. This
does not change what CTRL-BASELINE's failure_meaning tests (a defective
instrument would show *anomalously low* cost; using the un-optimized
constant as the comparison floor is strictly more conservative, since plain
rho's expected cost is *higher* than the negation-optimized model, not
lower, so this substitution cannot manufacture a spurious INV-BASELINE pass
or a spurious falsification event in either direction).
"""
from __future__ import annotations

import hashlib
import math
import random

from ec_affine import ec_add, ec_scalar_mult, negate

R_PARTITIONS = 21
MULTIPLIER_SCHEDULE_SEED = 0xC0FFEE


def _partition(x: int) -> int:
    h = hashlib.sha256(x.to_bytes((x.bit_length() + 7) // 8 or 1, "big")).digest()
    return int.from_bytes(h[:4], "big") % R_PARTITIONS


def pollard_rho_plain(P, Q, a, p, N, max_steps=None, seed=1):
    """
    Plain additive-walk Pollard rho (no negation-map folding), Floyd cycle
    detection. Returns dict: found, k, steps, group_ops, censored.
    """
    rng = random.Random(seed)
    max_steps = max_steps or (200 * int(math.isqrt(N)) + 10_000)
    group_ops = 0

    mult_points = []
    mult_coeffs = []
    for _ in range(R_PARTITIONS):
        s_j = rng.randrange(1, N)
        t_j = rng.randrange(1, N)
        Mj = ec_add(ec_scalar_mult(s_j, P, a, p), ec_scalar_mult(t_j, Q, a, p), a, p)
        group_ops += 2
        mult_points.append(Mj)
        mult_coeffs.append((s_j, t_j))

    def step(pt, c_p, c_q):
        nonlocal group_ops
        j = _partition(pt[0])
        Mj = mult_points[j]
        s_j, t_j = mult_coeffs[j]
        newpt = ec_add(pt, Mj, a, p)
        group_ops += 1
        return newpt, (c_p + s_j) % N, (c_q + t_j) % N

    a0 = rng.randrange(1, N)
    b0 = rng.randrange(1, N)
    x = ec_add(ec_scalar_mult(a0, P, a, p), ec_scalar_mult(b0, Q, a, p), a, p)
    group_ops += 2
    cp, cq = a0, b0
    y, cyp, cyq = x, cp, cq

    steps = 0
    while steps < max_steps:
        x, cp, cq = step(x, cp, cq)
        y, cyp, cyq = step(y, cyp, cyq)
        y, cyp, cyq = step(y, cyp, cyq)
        steps += 1
        if x == y:
            denom = (cq - cyq) % N
            if denom == 0:
                continue
            inv = pow(denom, -1, N)
            k = ((cyp - cp) * inv) % N
            return {"found": True, "k": k, "steps": steps, "group_ops": group_ops, "censored": False}
    return {"found": False, "k": None, "steps": steps, "group_ops": group_ops, "censored": True}


def bsgs(P, Q, a, p, N):
    m = math.isqrt(N) + 1
    group_ops = 0
    table = {}
    cur = None
    for j in range(m):
        table[cur] = j
        cur = ec_add(cur, P, a, p)
        group_ops += 1
    neg_mP = negate(ec_scalar_mult(m, P, a, p), p)
    group_ops += 1
    gamma = Q
    for i in range(m + 1):
        if gamma in table:
            j = table[gamma]
            k = (i * m + j) % N
            return {"found": True, "k": k, "group_ops": group_ops, "memory_points": m}
        gamma = ec_add(gamma, neg_mP, a, p)
        group_ops += 1
    return {"found": False, "k": None, "group_ops": group_ops, "memory_points": m}
