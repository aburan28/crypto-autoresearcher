"""
CTRL-PLANTED-PATH construction, per specification.yaml
inputs.planted_path_construction.

Draws a curve satisfying E1 (anomalous) by the same deterministic seeded
predicate machinery as sampler.py (not hand-picked), then attempts to walk
a short random forward chain of ell_0=3-isogeny steps to a generic-looking
E_rand, recording the exact forward chain so the construction is fully
auditable. E1 is used rather than E2/E3 because it has a verified, exact,
poly-time special-curve solver (sssa.py) implemented in this driver; E3 is
vacuously inapplicable to prime-field curves (predicates.py), and E2 is not
planted here (a full MOV pairing solver is out of this experiment's
implementation scope -- see implementation.md protocol_deviations).

TWO LEMMAS, discovered during implementation and recorded here (not
silently absorbed) because they determine whether a genuine multi-step
forward chain is even mathematically possible for this control:

LEMMA 1 (ell_0=2 is universally impossible for E1). For E1 (N=p), trace
t = p+1-N = 1 always. A rational 2-torsion point exists iff X^2-tX+p has a
root mod 2; for odd p and odd t=1, this is X^2+X+1 mod 2, the UNIQUE
irreducible quadratic over F_2. So no anomalous curve, over any odd prime,
ever has rational 2-torsion (isogeny2.py's step prime is useless here).

LEMMA 2 (ell_0=3 works for E1 only when p == 1 mod 3). A degree-3 kernel
does not need a rational POINT (isogeny3.py), only a Frobenius-fixed root
of the 3-division polynomial, which exists iff X^2-tX+p has a root mod 3.
With t=1 fixed (E1), and p mod 3 in {1,2} (p=3 is impossible at these
sizes): for p == 2 (mod 3), solving lambda + p/lambda == 1 (mod 3) over
lambda in {1,2} has NO solution (checked exhaustively; matches the general
fact -- also verified empirically across this experiment's actual census
population in the executor's working notes -- that root-existence for
prime-order curves at p==2 mod 3 requires N == 0 mod 3, impossible for
prime N, and t=1 is exactly the E1 case of that same general obstruction).
For p == 1 (mod 3), lambda=2 solves it (2 + 1/2 == 2+2 == 1 mod 3), so a
root exists. CONSEQUENCE: at this experiment's 20-bit and 24-bit primes
(both == 2 mod 3), a genuine forward chain is impossible and this driver
plants at chain_len=0 (still satisfying every explicit sub-condition of
CTRL-PLANTED-PATH's description: a degree-0 path is found within budget,
the solver runs, the log pulls back trivially, the certificate verifies).
At the 28-bit prime (== 1 mod 3), a genuine chain IS attempted and used
when construction succeeds.
"""
from __future__ import annotations
from .curve_order import compute_group_order, verify_group_order
from .isogeny3 import psi_3_roots, isogenous_curve_3
from .sampler import field_prime_for_bits, j_invariant
from .ecc import seeded_rng
from .predicates import classify


def find_anomalous_curve(p: int, seed_rng, max_attempts: int = 200000):
    for attempt in range(max_attempts):
        a = seed_rng.randrange(0, p)
        b = seed_rng.randrange(0, p)
        j = j_invariant(a, b, p)
        if j is None or j == 0 or j == (1728 % p):
            continue
        order_rng = seeded_rng(a, b, p, "order")
        try:
            N, ctr, npts = compute_group_order(a, b, p, order_rng)
        except RuntimeError:
            continue
        if N == p:
            assert verify_group_order(N, a, b, p, seeded_rng(a, b, p, "verify"), trials=3)
            return {"a": a, "b": b, "N": N, "attempt": attempt}
    raise RuntimeError(f"no anomalous curve found for p={p} within {max_attempts} attempts")


def walk_forward_chain(a0: int, b0: int, p: int, chain_len: int, walk_rng):
    """Walk `chain_len` genuine 3-isogeny steps from (a0,b0) (see Lemma 2:
    only possible when Frobenius has an eigenvalue mod 3, which for E1
    requires p == 1 mod 3), choosing a random available root at each step.
    chain_len=0 always succeeds trivially (no steps). Returns the full
    chain (list of {a,b[,kernel_x0]} per step, index 0 = origin) or raises
    RuntimeError if a dead end is hit before chain_len steps."""
    chain = [{"a": a0, "b": b0}]
    cur_a, cur_b = a0, b0
    for step in range(chain_len):
        roots0 = psi_3_roots(cur_a, cur_b, p)
        if not roots0:
            raise RuntimeError(f"dead end at step {step}: no rational 3-isogeny kernel")
        x0 = walk_rng.choice(roots0)
        a3, b3 = isogenous_curve_3(cur_a, cur_b, p, x0)
        chain.append({"a": a3, "b": b3, "kernel_x0": x0})
        cur_a, cur_b = a3, b3
    return chain


def construct_planted_instance(bit_size: int, master_seed: int, chain_len: int, k_max: int, max_restarts: int = 20):
    """Returns dict with: p, special_curve {a,b,N}, chain (list), E_rand
    {a,b}, forward_degree (3**achieved_chain_len), achieved_chain_len,
    requested_chain_len, and the restarts used. If a genuine chain of the
    REQUESTED length cannot be constructed within max_restarts (expected at
    bit sizes where Lemma 2's p mod 3 condition fails), this falls back to
    chain_len=0 and reports achieved_chain_len=0 explicitly -- never
    silently substitutes a shorter chain without disclosing it in the
    returned record."""
    p = field_prime_for_bits(bit_size)
    # Lemma 2 (module docstring): a genuine chain_len>0 walk from E1 is
    # possible only when p == 1 (mod 3); this is a fixed property of p, not
    # of which anomalous curve is drawn, so if it fails there is no value
    # in retrying find_anomalous_curve up to max_restarts times (each
    # retry costs a full O(p^{1/4}) search) -- go straight to the
    # chain_len=0 fallback instead of wasting the run's time budget
    # rediscovering a proven fact empirically.
    if chain_len > 0 and p % 3 != 1:
        seed_rng = seeded_rng(master_seed, bit_size, "planted-origin", 0)
        special = find_anomalous_curve(p, seed_rng)
        chain = [{"a": special["a"], "b": special["b"]}]
        return {
            "p": p,
            "special_curve": special,
            "chain": chain,
            "e_rand": {"a": special["a"], "b": special["b"]},
            "forward_degree": 1,
            "chain_len": 0,
            "requested_chain_len": chain_len,
            "achieved_chain_len": 0,
            "restarts_used": 0,
            "fallback_to_chain_len_0": True,
            "fallback_reason": f"p={p} % 3 = {p % 3} != 1; Lemma 2 proves chain_len>0 is impossible for E1 here",
        }
    for restart in range(max_restarts):
        seed_rng = seeded_rng(master_seed, bit_size, "planted-origin", restart)
        try:
            special = find_anomalous_curve(p, seed_rng)
        except RuntimeError:
            continue
        walk_rng = seeded_rng(master_seed, bit_size, "planted-walk", restart)
        try:
            chain = walk_forward_chain(special["a"], special["b"], p, chain_len, walk_rng)
        except RuntimeError:
            continue
        e_rand = chain[-1]
        return {
            "p": p,
            "special_curve": special,
            "chain": chain,
            "e_rand": {"a": e_rand["a"], "b": e_rand["b"]},
            "forward_degree": 3 ** chain_len,
            "chain_len": chain_len,
            "requested_chain_len": chain_len,
            "achieved_chain_len": chain_len,
            "restarts_used": restart,
            "fallback_to_chain_len_0": False,
            "fallback_reason": None,
        }
    # fall back to chain_len=0, per Lemma 1/2 this is expected at bit sizes
    # where p mod 3 != 1 (see module docstring); disclosed explicitly, not
    # silently substituted
    seed_rng = seeded_rng(master_seed, bit_size, "planted-origin", 0)
    special = find_anomalous_curve(p, seed_rng)
    chain = [{"a": special["a"], "b": special["b"]}]
    return {
        "p": p,
        "special_curve": special,
        "chain": chain,
        "e_rand": {"a": special["a"], "b": special["b"]},
        "forward_degree": 1,
        "chain_len": 0,
        "requested_chain_len": chain_len,
        "achieved_chain_len": 0,
        "restarts_used": max_restarts,
        "fallback_to_chain_len_0": True,
        "fallback_reason": f"chain_len={chain_len} not achieved within {max_restarts} restarts despite p%3==1",
    }
